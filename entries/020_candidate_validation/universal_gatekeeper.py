#!/usr/bin/env python3
"""
Universal Gatekeeper (Entry 020 – v1.0 CLEAN)
Deterministic, contract-safe, physics-gated validator.
"""

import os
import json
import argparse
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski

CATALOG = os.path.expanduser("~/control-atlas/library/pocket_catalog")
GRAMMAR_PATH = os.path.join(CATALOG, "pan_target_grammar.json")

# -----------------------------
# Helpers
# -----------------------------

def load_json(path):
    with open(path) as f:
        return json.load(f)

def normalize(status, reasons=None, metrics=None):
    return {
        "status": status,
        "reasons": reasons or [],
        "metrics": metrics or {}
    }

# -----------------------------
# Grammar + Physics
# -----------------------------

def load_grammar():
    return load_json(GRAMMAR_PATH)

def load_physics(target):
    path = os.path.join(CATALOG, target, "physics_metrics.json")
    if not os.path.exists(path):
        return None
    data = load_json(path)
    return data if data.get("status") == "computed" else None

def get_rules(target):
    grammar = load_grammar()
    pred_path = os.path.join(CATALOG, target, "grammar_prediction.json")

    if os.path.exists(pred_path):
        pred = load_json(pred_path)
        cls = pred.get("pocket_class")
        if cls and cls in grammar["class_specific_rules"]:
            return grammar["class_specific_rules"][cls]

    return {
        "mw_range": [300, 600],
        "polar_tolerance": "medium"
    }

# -----------------------------
# Validation
# -----------------------------

def validate(smiles, target):
    physics = load_physics(target)
    if not physics:
        return normalize(
            "UNSUPPORTED_TARGET",
            ["No physics computed for target"]
        )

    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return normalize("ERROR", ["Invalid SMILES"])

    rules = get_rules(target)

    mw = Descriptors.MolWt(mol)
    hbd = Lipinski.NumHDonors(mol)

    reasons = []
    lo, hi = rules.get("mw_range", [0, 2000])
    if not (lo <= mw <= hi):
        reasons.append(f"MW {mw:.1f} outside {lo}-{hi}")

    if rules.get("polar_tolerance") == "low" and hbd > 2:
        reasons.append(f"HBD {hbd} exceeds low-polar tolerance")

    status = "VALID" if not reasons else "REJECT"
    return normalize(status, reasons, {"mw": mw, "hbd": hbd})

# -----------------------------
# CLI
# -----------------------------

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--target", required=True)
    p.add_argument("--smiles", required=True)
    args = p.parse_args()

    res = validate(args.smiles, args.target)

    print(f"Target: {args.target}")
    print(f"Verdict: {res['status']}")
    for r in res["reasons"]:
        print(f"  X {r}")
