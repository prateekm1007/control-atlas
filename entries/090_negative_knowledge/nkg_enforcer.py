import json, jsonschema, os

SCHEMA_FILE = "nkg_schema_NKG-TAX-1.0.json"

def validate_entry(entry, db=None):
    if not os.path.exists(SCHEMA_FILE):
        raise FileNotFoundError("❌ SOVEREIGNTY BREACH: Schema file missing.")
    with open(SCHEMA_FILE, 'r') as f:
        schema = json.load(f)
    try:
        jsonschema.validate(instance=entry, schema=schema)
        if entry['forensics']['time_ns'] > entry['context']['simulation_duration_ns']:
            print("❌ GOVERNANCE FAIL: Failure time exceeds simulation duration.")
            return False
        if db is not None:
            if any(e["uuid"] == entry["uuid"] for e in db):
                print(f"❌ GOVERNANCE FAIL: Duplicate UUID detected.")
                return False
            prev_ranks = [e["severity_rank"] for e in db if e["design_id"] == entry["design_id"]]
            if prev_ranks and entry["severity_rank"] < max(prev_ranks):
                print(f"❌ GOVERNANCE FAIL: Severity regression detected.")
                return False
        print(f"✅ GOVERNANCE PASS: {entry['uuid']}")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ GOVERNANCE FAIL: {e.message}")
        return False

def commit_entry(entry, db_path):
    db = []
    if os.path.exists(db_path):
        with open(db_path, "r") as f:
            db = json.load(f)
    if validate_entry(entry, db):
        db.append(entry)
        tmp = db_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(db, f, indent=2)
        os.replace(tmp, db_path)
        return True
    return False
