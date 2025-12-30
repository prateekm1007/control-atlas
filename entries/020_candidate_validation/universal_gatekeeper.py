#!/usr/bin/env python3
"""
Universal Gatekeeper (Entry 020 - Generalized)
Accepts ANY target with computed physics and validates candidates.
"""

import sys
import os
import json
import argparse
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski

CATALOG = os.path.expanduser("~/control-atlas/library/pocket_catalog")
GRAMMAR = os.path.join(CATALOG, "pan_target_grammar.json")

def load_grammar():
    with open(GRAMMAR) as f: return json.load(f)

def get_target_rules(target_name):
    grammar = load_grammar()
    # Check if target has specific class prediction
    pred_path = os.path.join(CATALOG, target_name, "grammar_prediction.json")
    if os.path.exists(pred_path):
        with open(pred_path) as f: pred = json.load(f)
        p_class = pred.get("pocket_class")
        if p_class and p_class in grammar["class_specific_rules"]:
            return grammar["class_specific_rules"][p_class]
    
    # Fallback to universal defaults
    return {
        "mw_range": [300, 600],
        "polar_tolerance": "medium"
    }

def validate(smiles, target):
    rules = get_target_rules(target)
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return {"status": "ERROR", "reason": "Invalid SMILES"}
    
    mw = Descriptors.MolWt(mol)
    hbd = Lipinski.NumHDonors(mol)
    
    reasons = []
    
    # MW Check
    min_mw, max_mw = rules.get("mw_range", [0, 1000])
    if not (min_mw <= mw <= max_mw):
        reasons.append(f"MW {mw:.1f} outside {min_mw}-{max_mw}")
        
    # Polar Check
    if rules.get("polar_tolerance") == "low" and hbd > 2:
        reasons.append(f"HBD {hbd} too high for low-polar pocket")
        
    status = "VALID" if not reasons else "REJECT"
    return {"status": status, "reasons": reasons, "metrics": {"mw": mw, "hbd": hbd}}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--smiles", required=True)
    args = parser.parse_args()
    
    res = validate(args.smiles, args.target)
    print(f"Target: {args.target}")
    print(f"Verdict: {res['status']}")
    if res['reasons']:
        for r in res['reasons']: print(f"  X {r}")
