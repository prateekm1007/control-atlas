import json, datetime, sys
from nkg_enforcer import commit_entry

def run_milestone(time_ns, tag, pe):
    entry = {
        "uuid": f"VAR_YRK_HEALTH_{time_ns}NS_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}Z",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "design_id": "VAR_YRK",
        "failure_class": "HEALTH_CHECK",
        "failure_tag": tag,
        "severity": "TRANSIENT",
        "severity_rank": 1,
        "confidence": 1.0,
        "taxonomy_ver": "NKG-TAX-1.0",
        "platform_ver": "v1.8.0-toscanini",
        "context": {
            "forcefield": "amber14-all", "solvent_model": "tip3pfb",
            "temperature_K": 310.0, "pH": 7.4, "ionic_strength_M": 0.15,
            "simulation_duration_ns": 10.0
        },
        "forensics": {
            "time_ns": float(time_ns),
            "roles": {"ligand": {}, "target": {}},
            "metric_snapshot": {"potential_energy": float(pe)}
        }
    }
    commit_entry(entry, "nkg_database.json")

print("⚖️ Recording Milestones...")
run_milestone(2.0, "STABLE_EQUILIBRATION", -2295599.09)
run_milestone(5.0, "PERSISTENT_SAMPLING", -2297598.20)
