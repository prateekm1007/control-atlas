import json, datetime
from nkg_enforcer import commit_entry

entry = {
    "uuid": f"VAR_YRK_NEAR_MISS_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}Z",
    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "design_id": "VAR_YRK",
    "failure_class": "INTERACTION_GEOMETRY",
    "failure_tag": "WARHEAD_NON_ENGAGEMENT",
    "severity": "NEAR_MISS",
    "severity_rank": 2,
    "confidence": 0.95,
    "override_justification": "Confidence reduced to 0.95 due to high stochastic variance in handshake distance vs stable energetic profile.",
    "taxonomy_ver": "NKG-TAX-1.0",
    "platform_ver": "v1.8.0-toscanini",
    "context": {
        "forcefield": "amber14-all", "solvent_model": "tip3pfb",
        "temperature_K": 310.0, "pH": 7.4, "ionic_strength_M": 0.15,
        "simulation_duration_ns": 10.0
    },
    "forensics": {
        "time_ns": 10.0,
        "roles": {
            "ligand": {"region": "CDR3", "resname": "ARG"},
            "target": {"protein": "KRAS", "resname": "ASP"}
        },
        "metric_snapshot": {
            "avg_rmsd_A": 6.21, "avg_handshake_A": 56.57
        }
    }
}

if commit_entry(entry, "nkg_database.json"):
    print("✅ SOVEREIGN NEAR_MISS RECORDED.")
