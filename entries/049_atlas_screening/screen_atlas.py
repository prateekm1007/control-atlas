#!/usr/bin/env python3
"""
Entry 049 — Atlas Screening (Evidence Scaling)
"""

import sys, json, glob, time
from pathlib import Path
from dataclasses import asdict

BASE = Path(__file__).resolve().parents[2] / "entries"
sys.path.insert(0, str(BASE / "040_unified_navigator"))
sys.path.insert(0, str(BASE / "043_proof_engine"))
sys.path.insert(0, str(BASE / "044_knowledge_graph"))

from navigator import UnifiedNavigator
from proof_generator import ProofEngine
from graph_builder import KnowledgeGraph

ATLAS_DIR = Path(__file__).resolve().parents[2] / "library/atlas_index"
KG_OUT = BASE / "044_knowledge_graph" / "atlas_kg.json"

def load_library(path):
    lib = []
    with open(path) as f:
        for line in f:
            smi, cid = line.strip().split()
            lib.append((cid, smi))
    return lib

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--lib", required=True)
    args = parser.parse_args()

    library = load_library(args.lib)
    targets = glob.glob(str(ATLAS_DIR / "*.json"))

    nav = UnifiedNavigator()
    prover = ProofEngine()
    kg = KnowledgeGraph()

    print(f"[*] Screening {len(library)} compounds × {len(targets)} targets")

    t0 = time.time()
    n = 0

    for tf in targets:
        with open(tf) as f:
            tgt = json.load(f)

        tid = tgt["uniprot_id"]
        pockets = tgt.get("pockets", [])
        if not pockets:
            continue

        for cid, smi in library:
            for p in pockets:
                chem = nav.chem.evaluate({"smiles": smi, "pocket_metrics": p})
                nav_res = {
                    "compound_id": cid,
                    "status": "BLOCKED" if chem.status == "FAIL" else "CLEARED",
                    "trace": {"physics": p, "chemistry": chem.metrics}
                }
                proof = prover.generate_proof(nav_res)
                kg.add_proof(tid, cid, asdict(proof))
                n += 1

        if n % 5000 == 0:
            print(f"    … {n} proofs")

    print(f"[+] Done: {n} proofs in {time.time() - t0:.1f}s")
    kg.export_json(KG_OUT)
    print(f"[+] Saved KG → {KG_OUT}")

if __name__ == "__main__":
    main()
