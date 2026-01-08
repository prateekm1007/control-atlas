import json
from .load_mdi import load_mdi

def violates_mdi(candidate):
    """
    candidate = {
      "target": "KRAS_G12D",
      "generator": "CHAI-1"
    }
    """
    for law in load_mdi():
        if (
            candidate.get("target") in law.get("condition", "")
            and candidate.get("generator") in law.get("condition", "")
        ):
            return law
    return None

if __name__ == "__main__":
    test = {"target": "KRAS_G12D", "generator": "CHAI-1"}
    hit = violates_mdi(test)
    if hit:
        print(f"⛔ BLOCKED by {hit['doctrine_id']}")
    else:
        print("✅ Candidate allowed")
