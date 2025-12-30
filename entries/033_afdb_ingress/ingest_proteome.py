#!/usr/bin/env python3
"""
Entry 033 — AlphaFold DB Ingress

1. Fetch PDBs (by UniProt ID list)
2. Filter by pLDDT (Global Confidence)
3. Run Entry 027 (Pocket Detection)
4. Save VALIDATED pockets to the Atlas Index
"""

import argparse
import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

BASE = Path(__file__).resolve().parents[2] / "entries"
sys.path.insert(0, str(BASE / "027_pocket_detection"))

from pocket_detector import PocketDetector
from fetch_afdb import fetch_structure

# Index Directory
ATLAS_DIR = Path(__file__).resolve().parents[2] / "library/atlas_index"
ATLAS_DIR.mkdir(parents=True, exist_ok=True)

def get_plddt_from_pdb(pdb_path):
    """Extract global pLDDT from AFDB file."""
    scores = []
    with open(pdb_path, 'r') as f:
        for line in f:
            if line.startswith("ATOM") and " CA " in line:
                try:
                    # AFDB puts pLDDT in B-factor col (60-66)
                    scores.append(float(line[60:66]))
                except: pass
    if not scores: return 0.0
    return sum(scores) / len(scores)

def process_protein(uniprot_id, data_dir, min_plddt=70.0):
    """Pipeline for a single protein."""
    
    # 1. Fetch
    pdb_path = fetch_structure(uniprot_id, data_dir)
    if not pdb_path:
        return {"id": uniprot_id, "status": "DOWNLOAD_FAILED"}
    
    # 2. Structure Confidence Check
    # AFDB uses 0-100 scale. Control Atlas uses 0-1 internal scale mostly, 
    # but let's normalize to 0-1 for the PocketDetector.
    raw_plddt = get_plddt_from_pdb(pdb_path)
    
    if raw_plddt < min_plddt:
        return {
            "id": uniprot_id, 
            "status": "SKIPPED_LOW_CONFIDENCE", 
            "plddt": raw_plddt
        }
    
    conf_normalized = raw_plddt / 100.0
    
    # 3. Pocket Detection (Entry 027)
    detector = PocketDetector(max_pockets=3)
    result = detector.detect(pdb_path, structure_confidence=conf_normalized)
    
    if result["status"] != "SUCCESS":
        return {"id": uniprot_id, "status": "POCKET_DETECTION_ERROR", "error": result["error"]}
    
    # 4. Filter & Index
    valid_pockets = [p for p in result["pockets"] if p["status"] == "VALIDATED"]
    
    if not valid_pockets:
        return {"id": uniprot_id, "status": "NO_DRUGGABLE_POCKETS", "candidates": len(result["pockets"])}
    
    # Save to Index
    index_entry = {
        "uniprot_id": uniprot_id,
        "plddt_global": raw_plddt,
        "pockets": valid_pockets
    }
    
    index_path = ATLAS_DIR / f"{uniprot_id}.json"
    with open(index_path, "w") as f:
        json.dump(index_entry, f, indent=2)
        
    return {
        "id": uniprot_id, 
        "status": "INDEXED", 
        "pockets": len(valid_pockets)
    }

def main():
    parser = argparse.ArgumentParser(description="AFDB Ingress")
    parser.add_argument("--ids", required=True, help="Text file with UniProt IDs (one per line)")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    with open(args.ids) as f:
        uniprot_ids = [line.strip() for line in f if line.strip()]
    
    print(f"[*] Processing {len(uniprot_ids)} targets from AlphaFold DB...")
    
    results = []
    # Sequential for safety in demo, ThreadPool for speed in prod
    for uid in uniprot_ids:
        print(f" -> Processing {uid}...")
        res = process_protein(uid, data_dir)
        results.append(res)
        print(f"    {res['status']}")
    
    indexed = sum(1 for r in results if r['status'] == 'INDEXED')
    print(f"\n[+] Ingress Complete. Indexed {indexed}/{len(uniprot_ids)} targets.")
    print(f"[+] Atlas location: {ATLAS_DIR}")

if __name__ == "__main__":
    main()
