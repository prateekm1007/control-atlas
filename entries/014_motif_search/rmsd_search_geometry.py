#!/usr/bin/env python3
"""
Entry #014b: Geometry-Only Motif Search
Blind sliding-window search using rigid-body superposition (Kabsch).
NO sequence alignment. NO homology assumptions.
"""

import os
import csv
from prody import parsePDB, fetchPDB, superpose, calcRMSD

# Paths
MOTIF_PATH = os.path.expanduser("~/control-atlas/library/motifs/M001_Switch_GTPase.pdb")
OUTPUT_CSV = os.path.expanduser("~/control-atlas/library/matches/M001_geometry_hits_014b.csv")
PDB_CACHE = os.path.expanduser("~/control-atlas/library/pdb_cache/")

# Blind scan candidates
CANDIDATES = [
    ("5P21", "A"),  # H-Ras (control)
    ("2RGN", "A"),  # RhoA
    ("1YZN", "A"),  # Ran
    ("1HUR", "A"),  # Arf1
    ("1UBQ", "A"),  # Ubiquitin (negative control)
]

RMSD_THRESHOLD = 2.0  # Å

def sliding_window_search(target_ca, motif_coords):
    target_coords = target_ca.getCoords()
    target_len = target_coords.shape[0]
    motif_len = motif_coords.shape[0]

    if target_len < motif_len:
        return float("inf"), -1

    best_rmsd = float("inf")
    best_start = -1

    for i in range(target_len - motif_len + 1):
        window = target_coords[i:i+motif_len]

        aligned_window, _ = superpose(window, motif_coords)
        rmsd = calcRMSD(aligned_window, motif_coords)

        if rmsd < best_rmsd:
            best_rmsd = rmsd
            best_start = i

    return best_rmsd, best_start

def main():
    os.makedirs(PDB_CACHE, exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    print(f"Loading motif: {MOTIF_PATH}")
    motif = parsePDB(MOTIF_PATH)
    motif_ca = motif.select("calpha")

    if motif_ca is None:
        raise RuntimeError("Motif contains no Cα atoms")

    motif_coords = motif_ca.getCoords()
    motif_len = motif_coords.shape[0]

    print(f"Motif length: {motif_len} residues\n")

    results = []

    print(f"{'TARGET':<8} | {'BEST RMSD (Å)':<14} | STATUS | START")
    print("-" * 50)

    for pdb_id, chain in CANDIDATES:
        try:
            pdb_file = fetchPDB(pdb_id, folder=PDB_CACHE)
            structure = parsePDB(pdb_file)
            target_ca = structure.select(f"chain {chain} and calpha")

            if target_ca is None:
                print(f"{pdb_id:<8} | N/A           | ERROR  | N/A")
                continue

            rmsd, start_idx = sliding_window_search(target_ca, motif_coords)
            status = "MATCH" if rmsd <= RMSD_THRESHOLD else "REJECT"

            print(f"{pdb_id:<8} | {rmsd:<14.2f} | {status:<6} | {start_idx}")

            results.append({
                "pdb_id": pdb_id,
                "chain": chain,
                "best_rmsd": round(rmsd, 3),
                "start_index": start_idx,
                "status": status
            })

        except Exception as e:
            print(f"{pdb_id:<8} | ERROR: {e}")

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["pdb_id", "chain", "best_rmsd", "start_index", "status"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults written to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
