import sys
from entries._094_mdi.check_candidate import violates_mdi

def plan_or_abort(candidate):
    hit = violates_mdi(candidate)
    if hit:
        print("⛔ PLANNER ABORT")
        print(f"   Violated Doctrine: {hit['doctrine_id']}")
        print(f"   Verdict: {hit['verdict']}")
        sys.exit(1)

    print("✅ PLANNER PASS")
    print("   No locked doctrine violated")
    return True

if __name__ == "__main__":
    # Example CLI usage
    # python3 planner_gate.py KRAS_G12D CHAI-1
    target = sys.argv[1]
    generator = sys.argv[2]

    plan_or_abort({
        "target": target,
        "generator": generator
    })
