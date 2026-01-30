"""
Hardened Contextual Bond Registry (v14.0.29).
Enforces residue-specific permissions for inter-residue bonding.
"""

# Global Element Pair Windows (Safe for Intra-Residue use)
GLOBAL_WINDOWS = {
    ("C", "C"): (1.20, 1.75),
    ("C", "N"): (1.20, 1.65),
    ("C", "O"): (1.10, 1.60),
    ("C", "S"): (1.60, 1.95),
    ("N", "O"): (1.10, 1.55),
    ("P", "O"): (1.40, 1.75),
}

# Context-Specific Windows (Only allowed between specific residue types)
CONTEXT_WINDOWS = {
    ("S", "S"): {
        "allowed_residues": ["CYS"],
        "window": (1.85, 2.25) # Disulfide Bridge
    },
    ("ZN", "N"): {
        "allowed_residues": ["HIS", "CYS"],
        "window": (1.80, 2.35) # Metal Coordination
    },
    ("ZN", "O"): {
        "allowed_residues": ["ASP", "GLU", "HOH"],
        "window": (1.80, 2.35)
    },
    ("MG", "O"): {
        "allowed_residues": ["ASP", "GLU", "HOH", "ATP", "ADP"],
        "window": (1.80, 2.45)
    }
}

def is_contextually_bonded(a1, a2, dist):
    """
    Sovereign check for chemical bonding.
    Determines if two atoms have 'Physical Permission' to be close.
    """
    e1, e2 = a1.element.upper(), a2.element.upper()
    r1, r2 = a1.res_name.upper(), a2.res_name.upper()
    pair = tuple(sorted([e1, e2]))

    # 1. Check Context-Specific Windows (The CSO Guard)
    if pair in CONTEXT_WINDOWS:
        rule = CONTEXT_WINDOWS[pair]
        # At least one atom must belong to the allowed residues
        if r1 in rule["allowed_residues"] or r2 in rule["allowed_residues"]:
            win_min, win_max = rule["window"]
            return win_min <= dist <= win_max
        return False # Element pair exists, but residue context is illegal

    # 2. Check Global Windows (For intra-residue or standard covalent)
    if pair in GLOBAL_WINDOWS:
        win_min, win_max = GLOBAL_WINDOWS[pair]
        return win_min <= dist <= win_max

    return False
