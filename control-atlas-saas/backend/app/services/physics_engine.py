import json
import subprocess
from pathlib import Path

CODEX = Path(__file__).parent.parent / "core" / "mdi_codex.json"

with open(CODEX) as f:
    MDI = json.load(f)

LAWS = MDI["laws"]

class SovereignEngine:
    @staticmethod
    def run_audit(file_path: str, target: str, binder: str):
        results = {"laws_violated": []}

        # TIER 0 — FORMAT CHECK
        if not file_path.endswith(".cif"):
            results["laws_violated"].append("LAW-001")
            return results

        # INVOKE SOVEREIGN JUDGE
        proc = subprocess.run(
            ["python3", "/app/tools/native_audit.py", file_path, "--target", target, "--binder", binder],
            capture_output=True, text=True
        )

        try:
            metrics = json.loads(proc.stdout)
        except:
            return {"laws_violated": ["ERR_JUDGE_TIMEOUT"]}

        # EXECUTABLE ENFORCEMENT
        for lid, law in LAWS.items():
            metric = law.get("metric")
            
            # Handling multi-metric logic (e.g. Score-Clearance)
            if isinstance(metric, list):
                if all(m in metrics for m in metric):
                    if metrics[metric[0]] > 80 and metrics[metric[1]] > 0:
                        results["laws_violated"].append(lid)
            
            # Handling threshold-based logic
            elif metric in metrics:
                val = metrics[metric]
                if "threshold_min" in law and val < law["threshold_min"]:
                    results["laws_violated"].append(lid)
                if "threshold_max" in law and val > law["threshold_max"]:
                    results["laws_violated"].append(lid)
                if "forbidden_range" in law:
                    lo, hi = law["forbidden_range"]
                    if lo <= val <= hi:
                        results["laws_violated"].append(lid)

        return results

    @staticmethod
    def calculate_verdict(metrics):
        if metrics["laws_violated"]:
            # If any VETO level laws are broken, return VETO
            for lid in metrics["laws_violated"]:
                if LAWS[lid]["action"] == "VETO":
                    return "PHYSICS_VETO", lid
            return "SOVEREIGN_PASS", metrics["laws_violated"][0] # FLAG/WARN
        return "SOVEREIGN_PASS", None
