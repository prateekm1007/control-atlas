#!/usr/bin/env python3
"""
Entry 028 — Structure Prediction Ingress

Swappable, uncertainty-aware structure prediction with mandatory caching.
Uses dynamic imports to bypass numeric entry directory constraints.
"""

import argparse
import json
import sys
import importlib.util
from pathlib import Path

# ---- Dynamic import helpers ----
BASE = Path(__file__).resolve().parent

def _load(module_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod

esmfold_mod = _load(
    BASE / "backends/esmfold.py",
    "entry028_esmfold"
)

cache_mod = _load(
    BASE / "backends/cache.py",
    "entry028_cache"
)

predict_structure = esmfold_mod.predict_structure
get_cached = cache_mod.get_cached
save_to_cache = cache_mod.save_to_cache
# --------------------------------

class StructureProvider:
    def __init__(self, backend="esmfold", cache_dir=None):
        self.backend = backend
        self.cache_dir = cache_dir or (BASE / "cache")

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
            sequence=sequence,
            pdb_string=result["pdb_string"],
            confidence_global=result["confidence_global"],
            confidence_per_residue=result["confidence_per_residue"],
            source=self.backend,
            cache_dir=self.cache_dir
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
    ap = argparse.ArgumentParser(description="Structure Prediction (Entry 028)")
    ap.add_argument("--sequence", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    sp = StructureProvider()
    out = sp.predict(args.sequence)

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(out)

if __name__ == "__main__":
    main()
