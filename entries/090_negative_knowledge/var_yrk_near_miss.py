import datetime
from nkg_enforcer import commit_entry

now = datetime.datetime.now(datetime.timezone.utc)

entry = {
    "uuid": f"VAR_YRK_PHYS_04_{now.strftime('%Y%m%d%H%M%S')}Z",
    "timestamp": now.isoformat().replace("+00:00", "Z"),
    "design_id": "VAR_YRK",
    "failure_class": "INTERACTION_GEOMETRY",
    "failure_tag": "STERIC_REPULSION_LAUNCH",
    "severity": "TERMINAL",
    "severity_rank": 3,
    "confidence": 0.99,
    "taxonomy_ver": "NKG-TAX-1.0",
    "platform_ver": "v1.8.0-toscanini",
    "context": {
        "forcefield": "amber14-all",
        "solvent_model": "tip3pfb",
        "temperature_K": 310.0,
        "pH": 7.4,
        "ionic_strength_M": 0.15,
        "simulation_duration_ns": 10.0
    },
    "forensics": {
        "time_ns": 0.001,
        "roles": {
            "ligand": "CDR3_WARHEAD_YRK",
            "target": "KRAS_G12D_INTERFACE"
        },
        "metric_snapshot": {
            "frame0_dist_A": 1.31,
            "final_dist_A": 56.57,
            "verdict": "STRICT_STERIC_CLASH"
        }
    },
    "override_justification": (
        "Initial heavy-atom separation of 1.31 Å constitutes a physical "
        "impossibility (steric overlap), triggering immediate repulsive "
        "forces and ballistic separation at simulation start."
    )
}

if commit_entry(entry, "nkg_database.json"):
    print("✅ SOVEREIGN REFUSAL RECORDED: STERIC_REPULSION_LAUNCH")
