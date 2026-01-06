import json, datetime, os

NKG_FILE = os.path.expanduser("~/control-atlas/entries/090_negative_knowledge/nkg_database.json")

def log_failure(design_id, gate_failed, metric_value, metadata=None):
    entry = {
        "timestamp": str(datetime.datetime.now()),
        "design_id": design_id,
        "gate": gate_failed,
        "value": metric_value,
        "metadata": metadata or {}
    }
    db = []
    if os.path.exists(NKG_FILE):
        try:
            with open(NKG_FILE, 'r') as f:
                db = json.load(f)
        except:
            db = []
    db.append(entry)
    with open(NKG_FILE, 'w') as f:
        json.dump(db, f, indent=2)
    print(f"💀 NKG UPDATED: {design_id} → {gate_failed}")
