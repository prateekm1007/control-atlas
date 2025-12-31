"""
Maps Biology context → Constraints
"""

from constraint import Constraint

def essentiality_constraint(score):
    threshold = 0.5
    margin = (score - threshold) / threshold

    status = "PASS" if score >= threshold else "FAIL"

    return Constraint(
        layer="Biology",
        parameter="Essentiality",
        threshold=threshold,
        actual=score,
        margin=round(margin, 3),
        status=status,
        collapses_space=True,
        provenance={
            "source": "DepMap",
            "logic": "Causal relevance"
        }
    )
