import importlib
def list_all_law_ids(): return [f"LAW-{i}" for i in [155, 160, 120, 182, 190, 195, 200, 210, 220, 230]]
def get_law_explanation(law_id):
    name = law_id.lower().replace("-", "_")
    try:
        mod = importlib.import_module(f"glossary.tier1.{name}")
        return mod.EXPLANATION
    except: return {"title": law_id, "principle": "Physical Invariant", "rationale": "Truth."}
