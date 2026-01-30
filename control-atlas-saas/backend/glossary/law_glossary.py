CANON = {
    "LAW-120": {"title": "Peptide Bond Sanity", "principle": "Covalent bond length (1.33A).", "rationale": "Peptide bonds are resonance hybrids. Lengths outside the 1.13A-1.53A range violate quantum mechanics."},
    "LAW-155": {"title": "Steric Clash Prohibition", "principle": "Atoms cannot overlap.", "rationale": "The Pauli exclusion principle forbids electron cloud overlap. Non-bonded atoms approaching closer than 2.0A create physically impossible geometry."},
    "LAW-160": {"title": "Backbone Continuity", "principle": "Consistent C-alpha spacing (~3.8A).", "rationale": "Deviations > 4.5A indicate a torn or hallucinated chain, physically impossible in a continuous polymer."},
    "LAW-182": {"title": "Hydrophobic Burial", "principle": "Non-polar residues must be buried.", "rationale": "Surface-exposed hydrophobic patches lead to immediate aggregation in solution."},
    "LAW-190": {"title": "Ring Planarity", "principle": "Aromatic rings must remain flat.", "rationale": "Delocalized pi-bonding enforces planarity. Non-planar rings indicate optimization failure."},
    "LAW-195": {"title": "Disulfide Geometry", "principle": "S-S distance approx 2.05A.", "rationale": "Incorrect geometry prevents proper folding and traps the design in non-functional states."},
    "LAW-200": {"title": "Cavity Collapse", "principle": "Functional pockets must exist.", "rationale": "Binding requires defined cavities. Pocket collapse renders the design dead."},
    "LAW-210": {"title": "Helix Crossing", "principle": "Canonical packing angles.", "rationale": "Ridges-into-grooves packing geometry constrains crossing angles."},
    "LAW-220": {"title": "Beta Strand Registry", "principle": "Precise H-bond alignment.", "rationale": "Beta-sheet stability requires spatial registry. Shifts destroy the network."},
    "LAW-230": {"title": "Atomic Valence", "principle": "Quantum valid coordination.", "rationale": "Atoms have fixed coordination numbers based on electron configuration."}
}
def list_all_law_ids(): return list(CANON.keys())
def get_law_explanation(law_id): return CANON.get(law_id, {"title": law_id, "principle": "N/A", "rationale": "N/A"})
