"""
Maps Chemistry metrics → Constraints
"""

from constraint import Constraint

def polarity_constraint(logp, pocket_hydro):
    # heuristic target logP range
    target = 4.0 if pocket_hydro > 0.6 else 2.0
    margin = 1 - abs(logp - target) / target

    status = "PASS" if margin > 0 else "FAIL"

    return Constraint(
        layer="Chemistry",
        parameter="PolarityMatch",
        threshold=target,
        actual=logp,
        margin=round(margin, 3),
        status=status,
        collapses_space=True,
        provenance={
            "pocket_hydrophobicity": pocket_hydro,
            "logic": "Energetic compatibility"
        }
    )
