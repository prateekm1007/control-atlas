#!/usr/bin/env python3
"""
Compute physics metrics for all cataloged pockets (Fixed)
"""

import os
import json
import numpy as np
from prody import fetchPDB, parsePDB

CATALOG = os.path.expanduser("~/control-atlas/library/pocket_catalog")
PDB_CACHE = os.path.expanduser("~/control-atlas/library/pdb_cache")

def compute_pocket_physics(pdb_id, chain, residues):
    try:
        pdb_file = fetchPDB(pdb_id, folder=PDB_CACHE)
        structure = parsePDB(pdb_file)
        
        res_str = " ".join([str(r) for r in residues])
        sel = structure.select(f"chain {chain} and resnum {res_str}")
        
        if sel is None or sel.numAtoms() == 0:
            # Try without chain specification
            sel = structure.select(f"resnum {res_str}")
            if sel is None or sel.numAtoms() == 0:
                return {"status": "failed", "error": "No atoms found for residues"}
        
        coords = sel.getCoords()
        
        # Volume
        try:
            from scipy.spatial import ConvexHull
            if len(coords) >= 4:
                hull = ConvexHull(coords)
                volume = hull.volume
            else:
                volume = 0
        except:
            volume = 0
        
        # Exposure
        all_atoms = structure.select("protein")
        if all_atoms is not None:
            all_coords = all_atoms.getCoords()
            exposure_scores = []
            for pc in coords:
                distances = np.linalg.norm(all_coords - pc, axis=1)
                n_neighbors = np.sum((distances > 0) & (distances < 8.0))
                exp = 100 - min(n_neighbors, 100)
                exposure_scores.append(exp)
            exposure = np.mean(exposure_scores)
        else:
            exposure = 0
        
        # Hydrophobicity
        HYDROPHOBIC = {"ALA", "VAL", "LEU", "ILE", "MET", "PHE", "TRP", "PRO"}
        ca_sel = structure.select(f"resnum {res_str} and name CA")
        if ca_sel and ca_sel.numAtoms() > 0:
            resnames = ca_sel.getResnames()
            hydro_frac = sum(1 for r in resnames if r in HYDROPHOBIC) / len(resnames) * 100
        else:
            hydro_frac = 0
        
        return {
            "volume_A3": round(volume, 1),
            "exposure": round(exposure, 2),
            "hydrophobic_pct": round(hydro_frac, 1),
            "atom_count": sel.numAtoms(),
            "status": "computed"
        }
        
    except Exception as e:
        return {"status": "failed", "error": str(e)}

def process_catalog():
    print("=== COMPUTING POCKET PHYSICS ===")
    
    success = 0
    failed = 0
    
    for entry in sorted(os.listdir(CATALOG)):
        frame_path = os.path.join(CATALOG, entry, "pocket_frame.json")
        physics_path = os.path.join(CATALOG, entry, "physics_metrics.json")
        
        if not os.path.exists(frame_path):
            continue
        
        with open(frame_path, "r") as f:
            frame = json.load(f)
        
        pdbs = frame["pocket"]["source_pdbs"]
        pdb_id = pdbs[0] if pdbs else None
        residues = frame["frame"]["lining_residues"]
        
        if not pdb_id or not residues:
            print(f"[SKIP] {entry}: Missing PDB or residues")
            continue
        
        print(f"Processing {entry} ({pdb_id})...")
        
        metrics = compute_pocket_physics(pdb_id, "A", residues)
        
        if metrics is None:
            metrics = {"status": "failed", "error": "Unknown error"}
        
        if metrics.get("status") == "computed":
            with open(physics_path, "w") as f:
                json.dump(metrics, f, indent=2)
            print(f"  [OK] Vol={metrics['volume_A3']}, Exp={metrics['exposure']}, Hydro={metrics['hydrophobic_pct']}%")
            success += 1
        else:
            with open(physics_path, "w") as f:
                json.dump(metrics, f, indent=2)
            print(f"  [FAIL] {metrics.get('error', 'Unknown')}")
            failed += 1
    
    print(f"\n=== COMPLETE ===")
    print(f"Success: {success}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    process_catalog()
