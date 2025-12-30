#!/usr/bin/env python3
"""
Entry 028 — Structure Prediction Ingress
"""

import argparse
import json
from pathlib import Path

from entries.028_structure_prediction.backends.esmfold import predict_structure
from entries.028_structure_prediction.backends.cache import get_cached, save_to_cache

class StructureProvider:
    def __init__(self, backend="esmfold", cache_dir=None):
        self.backend = backend
        self.cache_dir = cache_dir or (Path(__file__).parent / "cache")

    def predict(self, sequence: str) -> dict:
        sequence = sequence.upper().strip()

        cached = get_cached(sequence, self.cache_dir)
        if cached:
            return cached

        if self.backend != "esmfold":
            return {
                "status": "ERROR",
                "pdb_path": None,
                "confidence_global": 0.0,
                "confidence_per_residue": [],
                "source": self.backend,
                "cached": False,
                "error": "Unknown backend"
            }

        result = predict_structure(sequence)
        if result["status"] != "SUCCESS":
            return {
                "status": "ERROR",
                "pdb_path": None,
                "confidence_global": 0.0,
                "confidence_per_residue": [],
                "source": self.backend,
                "cached": False,
                "error": result["error"]
            }

        pdb_path = save_to_cache(
            sequence,
            result["pdb_string"],
            result["confidence_global"],
            result["confidence_per_residue"],
            self.backend,
            self.cache_dir
        )

        return {
            "status": "SUCCESS",
            "pdb_path": pdb_path,
            "confidence_global": result["confidence_global"],
            "confidence_per_residue": result["confidence_per_residue"],
            "source": self.backend,
            "cached": False,
            "error": None
        }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sequence", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    sp = StructureProvider()
    out = sp.predict(args.sequence)

    print(json.dumps(out, indent=2) if args.json else out)

if __name__ == "__main__":
    main()
