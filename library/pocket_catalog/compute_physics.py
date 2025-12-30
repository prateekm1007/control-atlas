#!/usr/bin/env python3
"""
Compute physics metrics (FIXED ATOM SELECTION)
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
        
        # Select ALL atoms for lining residues (not just backbone)
        res_str = " ".join([str(r) for r in residues])
        # Try specific chain first
        sel = structure.select(f"chain {chain} and resnum {res_str}")
        
        if sel is None or sel.numAtoms() < 10:
            # Fallback: ignore chain if selection is empty/tiny
            sel = structure.select(f"resnum {res_str}")
            
        if sel is None or sel.numAtoms() < 10:
            return {"status": "failed", "error": f"Insufficient atoms: {sel.numAtoms() if sel else 0}"}
        
        coords = sel.getCoords()
        
        # Volume (Convex Hull of all atoms)
        try:
            from scipy.spatial import ConvexHull
            hull = ConvexHull(coords)
            volume = hull.volume
        except:
            volume = 0
        
        # Exposure (SASA proxy)
        all_atoms = structure.select("protein")
        all_coords = all_atoms.getCoords()
        exposure_scores = []
        # Sample subset for speed if too large
        sample_coords = coords[::5] if len(coords) > 500 else coords
        
        for pc in sample_coords:
            distances = np.linalg.norm(all_coords - pc, axis=1)
            n_neighbors = np.sum((distances > 0) & (distances < 8.0))
            # Fewer neighbors = more exposed
            exp = max(0, 100 - n_neighbors * 2) # Adjusted scaling
            exposure_scores.append(exp)
        exposure = np.mean(exposure_scores)
        
        # Hydrophobicity
        HYDROPHOBIC = {"ALA", "VAL", "LEU", "ILE", "MET", "PHE", "TRP", "PRO", "TYR"}
        res_names = set(sel.getResnames())
        hydro_count = sum(1 for r in res_names if r in HYDROPHOBIC)
        hydro_frac = (hydro_count / len(res_names)) * 100 if res_names else 0
        
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
    print("=== COMPUTING POCKET PHYSICS (FIXED) ===")
    
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
        
        if not pdb_id: continue
        
        print(f"Processing {entry} ({pdb_id})...")
        metrics = compute_pocket_physics(pdb_id, "A", residues)
        
        if metrics.get("status") == "computed":
            with open(physics_path, "w") as f:
                json.dump(metrics, f, indent=2)
            print(f"  [OK] Vol={metrics['volume_A3']}, Hydro={metrics['hydrophobic_pct']}%")
            success += 1
        else:
            print(f"  [FAIL] {metrics.get('error')}")
            failed += 1
            
    print(f"Success: {success}, Failed: {failed}")

if __name__ == "__main__":
    process_catalog()
