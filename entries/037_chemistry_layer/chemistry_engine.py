#!/usr/bin/env python3
"""
Entry 037 — Chemistry Layer: Tractability & Compatibility
"""

import sys
from pathlib import Path
from dataclasses import dataclass

# Link to Architecture
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "entries/036_unified_architecture"))
from core_interfaces import Layer, Constraint

from rdkit import Chem
from rdkit.Chem import QED, Descriptors
from conformer_gen import generate_conformers

@dataclass
class ChemistryResult:
    status: str # PASS, FAIL
    reasons: list
    metrics: dict

class ChemistryLayer(Layer):
    """
    Evaluates:
    1. Intrinsic Tractability (QED, Alerts)
    2. Pocket Compatibility (Polarity Match)
    3. Conformer Feasibility (Dynamics)
    """
    
    def evaluate(self, context: dict) -> ChemistryResult:
        smiles = context.get("smiles")
        pocket_metrics = context.get("pocket_metrics", {})
        
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return ChemistryResult("FAIL", ["Invalid SMILES"], {})
            
        reasons = []
        metrics = {}
        
        # 1. Intrinsic Tractability (QED)
        qed = QED.qed(mol)
        metrics["qed"] = round(qed, 2)
        if qed < 0.2:
            reasons.append(f"QED too low ({qed:.2f})")
            
        # 2. Molecular Weight vs Pocket Volume
        mw = Descriptors.MolWt(mol)
        metrics["mw"] = round(mw, 1)
        pocket_vol = pocket_metrics.get("volume", 500.0) # Default if missing
        
        # Heuristic: Ligand MW ~ 0.5-1.5x Pocket Vol (rough density approx)
        if mw > pocket_vol * 1.5:
            reasons.append(f"Molecule too large for pocket ({mw} vs {pocket_vol})")
            
        # 3. Polarity Mismatch (LogP vs Hydrophobicity)
        logp = Descriptors.MolLogP(mol)
        metrics["logp"] = round(logp, 2)
        pocket_hydro = pocket_metrics.get("hydrophobic_pct", 0.5)
        
        # If pocket is very polar (low hydro), LogP should be low
        if pocket_hydro < 0.3 and logp > 4.0:
            reasons.append(f"Greasy molecule in polar pocket (LogP {logp} vs Hydro {pocket_hydro})")
            
        # 4. Dynamics Check (Conformers)
        # If rigid constraints failed, check if ANY conformer could plausibly fit
        # (Simplified: Just ensure we CAN generate conformers)
        confs = generate_conformers(mol, num_confs=5)
        if not confs:
            reasons.append("Sterically impossible (no valid conformers)")
            
        status = "FAIL" if reasons else "PASS"
        return ChemistryResult(status, reasons, metrics)

# CLI for testing
if __name__ == "__main__":
    test_smiles = "CC(C)(C)NC1=NC=NC2=C1N=CN2" # Sotorasib core
    test_pocket = {"volume": 400.0, "hydrophobic_pct": 0.6}
    
    engine = ChemistryLayer()
    result = engine.evaluate({"smiles": test_smiles, "pocket_metrics": test_pocket})
    print(result)
