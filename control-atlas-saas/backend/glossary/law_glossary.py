import importlib
def list_all_law_ids(): return ["LAW-155", "LAW-160", "LAW-120", "LAW-182", "LAW-190", "LAW-195", "LAW-200", "LAW-210", "LAW-220", "LAW-230"]
def get_law_explanation(law_id):
    name = law_id.lower().replace("-", "_")
    try:
        mod = importlib.import_module(f"glossary.tier1.{name}")
        return mod.EXPLANATION
    except: return {"title": law_id, "principle": "Invariant", "rationale": "Truth."}
