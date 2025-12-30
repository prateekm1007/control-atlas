#!/usr/bin/env python3
import os
import csv
import subprocess

CATALOG = os.path.expanduser("~/control-atlas/library/pocket_catalog")
DRIVERS = os.path.join(CATALOG, "cosmic_drivers_v1.csv")
INGEST = os.path.join(CATALOG, "ingest_target.py")

def batch_ingest():
    print("=== BATCH POCKET INGESTION ===")
    if not os.path.exists(DRIVERS):
        print(f"Missing: {DRIVERS}")
        return
    if not os.path.exists(INGEST):
        print(f"Missing: {INGEST}")
        return
    with open(DRIVERS, "r") as f:
        reader = csv.DictReader(f)
        targets = list(reader)
    print(f"Processing {len(targets)} targets...")
    success = 0
    for t in targets:
        cmd = ["python3", INGEST, "--target", t["target"], "--mutation", t["mutation"], "--domain", t["domain"], "--uniprot", t["uniprot"], "--pdbs", t["pdbs"], "--lining", t["lining"]]
        try:
            subprocess.run(cmd, check=True)
            print(f"[OK] {t['target']}_{t['mutation']}")
            success += 1
        except:
            print(f"[FAIL] {t['target']}_{t['mutation']}")
    print(f"Complete: {success} targets")

if __name__ == "__main__":
    batch_ingest()
