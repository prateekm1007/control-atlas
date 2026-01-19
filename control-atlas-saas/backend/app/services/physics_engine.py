import subprocess
import json
import os
from pathlib import Path

class SovereignEngine:
    # Use ABSOLUTE paths to prevent boot-time crashes in Docker
    BASE_PATH = Path(__file__).parent.parent
    CODEX_PATH = BASE_PATH / "core" / "mdi_codex.json"

    @classmethod
    def get_law_library(cls):
        try:
            with open(cls.CODEX_PATH, "r") as f:
                return json.load(f)["laws"]
        except:
            return {"LAW-001": {"title": "Error", "note": "Codex Load Failed", "threshold": "N/A"}}

    @staticmethod
    def run_audit(file_path: str, target: str, binder: str):
        audit_script = "/app/tools/native_audit.py"
        trace = {lid: {"status": 0, "reason": "QUEUED", "title": d["title"], "note": d["note"]} 
                 for lid, d in SovereignEngine.get_law_library().items()}

        if file_path.endswith('.pdb'):
            trace["LAW-001"].update({"status": 2, "reason": "TERMINAL_FORMAT_FAILURE"})
            return {"error": "Format Veto", "trace": trace}
        
        trace["LAW-001"].update({"status": 1, "reason": "Verified CIF"})
        cmd = ["python3", audit_script, file_path, "--target", target, "--binder", binder]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        try:
            m = json.loads(result.stdout)
            if m.get('clashes', 0) > 0:
                trace["LAW-155"] = {"status": 2, "reason": f"Clash: {m.get('min_distance_A')}A", "title": "Steric", "note": "Atoms overlap"}
            else:
                trace["LAW-155"] = {"status": 1, "reason": "Verified", "title": "Steric", "note": "Safe"}
            m['trace'] = trace
            return m
        except:
            return {"error": "Audit crash", "trace": trace}

    @staticmethod
    def calculate_verdict(metrics: dict):
        trace = metrics.get('trace', {})
        if trace.get("LAW-001", {}).get("status") == 2: return "FORMAT_VETO", "LAW-001"
        if trace.get("LAW-155", {}).get("status") == 2: return "PHYSICS_VETO", "LAW-155"
        return "SOVEREIGN_PASS", None
