#!/usr/bin/env python3
"""
Entry 033 — AlphaFold DB Ingress & Indexing

1. Fetch PDBs
2. Filter by global pLDDT (>70)
3. Detect pockets (Entry 027)
4. Index VALIDATED/CANDIDATE pockets
"""

import argparse
import json
import sys
import importlib.util
from pathlib import Path

# Dynamic import helper
def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

BASE = Path(__file__).resolve().parents[2] / "entries"

# Load Entry 027
pocket_module = load_module(
    "pocket_detector", 
    BASE / "027_pocket_detection" / "pocket_detector.py"
)
PocketDetector = pocket_module.PocketDetector

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
    raw_plddt = get_plddt_from_pdb(pdb_path)
    
    if raw_plddt < min_plddt:
        return {
            "id": uniprot_id, 
            "status": "SKIPPED_LOW_CONFIDENCE", 
            "plddt": raw_plddt
        }
    
    conf_normalized = raw_plddt / 100.0
    
    # 3. Pocket Detection (Entry 027)
    detector = PocketDetector(max_pockets=5)
    result = detector.detect(pdb_path, structure_confidence=conf_normalized)
    
    if result["status"] != "SUCCESS":
        return {"id": uniprot_id, "status": "POCKET_DETECTION_ERROR", "error": result["error"]}
    
    # 4. Filter & Index (Keep VALIDATED and CANDIDATE)
    indexable_pockets = [
        p for p in result["pockets"] 
        if p["status"] in ("VALIDATED", "CANDIDATE")
    ]
    
    if not indexable_pockets:
        return {"id": uniprot_id, "status": "NO_INDEXABLE_POCKETS", "candidates": len(result["pockets"])}
    
    # Save to Index
    index_entry = {
        "uniprot_id": uniprot_id,
        "plddt_global": raw_plddt,
        "pockets": indexable_pockets,
        "source": "AlphaFoldDB",
        "fpocket_version": "4.0", # Hardcoded for now, should be dynamic
        "ingest_timestamp": "2025-12-31" 
    }
    
    index_path = ATLAS_DIR / f"{uniprot_id}.json"
    with open(index_path, "w") as f:
        json.dump(index_entry, f, indent=2)
        
    return {
        "id": uniprot_id, 
        "status": "INDEXED", 
        "pockets": len(indexable_pockets)
    }

def main():
    parser = argparse.ArgumentParser(description="AFDB Ingress")
    parser.add_argument("--ids", required=True, help="Text file with UniProt IDs")
    args = parser.parse_args()
    
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    with open(args.ids) as f:
        uniprot_ids = [line.strip() for line in f if line.strip()]
    
    print(f"[*] Processing {len(uniprot_ids)} targets from AlphaFold DB...")
    
    results = []
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
