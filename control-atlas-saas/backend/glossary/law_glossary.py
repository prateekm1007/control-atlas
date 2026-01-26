import os, importlib, sys
from pathlib import Path

def list_all_law_ids():
    return [f"LAW-{i}" for i in [155, 160, 120, 182, 190, 195, 200, 210, 220, 230]]

def get_law_explanation(law_id: str):
    defs = {
        "LAW-155": {"title": "Steric Clash Prohibition", "summary": "Atoms cannot overlap overlapping space.", "rationale": "The Pauli exclusion principle forbids electron cloud overlap. Non-bonded atoms approaching closer than 2.5A create physically impossible geometry."},
        "LAW-160": {"title": "Backbone Continuity", "summary": "Fixed C-Alpha spacing integrity.", "rationale": "Resonance stabilization and planarity fix Ca-Ca distance at ~3.8A. Deviations indicate a torn protein chain."},
        "LAW-120": {"title": "Peptide Bond Sanity", "summary": "Valid covalent bond length.", "rationale": "Peptide bonds are resonance hybrids (1.33A). Lengths outside 1.13A-1.53A violate quantum mechanics."}
    }
    return defs.get(law_id, {"title": f"{law_id} Invariant", "summary": "Universal Physical Truth", "rationale": "Non-negotiable physical constraint."})
