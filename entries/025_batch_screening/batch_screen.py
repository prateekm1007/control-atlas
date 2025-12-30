#!/usr/bin/env python3
"""
Entry 025 — Batch Compound Screening (High-Throughput)

Orchestrates large-scale compound validation using the
Universal Gatekeeper (Entry 020) as the sole decision engine.

MECHANISM:
Uses importlib to dynamically load Entry 020 (bypassing '020_' import syntax issues).
This allows loading the Physics Engine ONCE and screening compounds in a tight loop.
"""

import argparse
import csv
import json
import sys
import os
import importlib.util
from pathlib import Path
from time import time

# --- Dynamic Import of Entry 020 ---
# We use importlib because '020_candidate_validation' is not a valid Python identifier.
GK_PATH = Path(__file__).resolve().parents[2] / "entries/020_candidate_validation/universal_gatekeeper.py"

try:
    spec = importlib.util.spec_from_file_location("universal_gatekeeper", GK_PATH)
    gk_module = importlib.util.module_from_spec(spec)
    sys.modules["universal_gatekeeper"] = gk_module
    spec.loader.exec_module(gk_module)
    UniversalGatekeeper = gk_module.UniversalGatekeeper
except Exception as e:
    sys.stderr.write(f"CRITICAL: Could not import UniversalGatekeeper from {GK_PATH}\n{e}\n")
    sys.exit(1)
# -----------------------------------

def parse_smi(smi_path):
    """Yields (compound_id, smiles) from a .smi file."""
    with open(smi_path, "r") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            smiles = parts[0]
            # Use provided ID or generate cmp_XXXXXX
            cid = parts[1] if len(parts) > 1 else f"cmp_{idx+1:06d}"
            yield cid, smiles

def main():
    ap = argparse.ArgumentParser(description="Batch compound screening via Universal Gatekeeper")
    ap.add_argument("--target", required=True, help="Target name (e.g. KRAS_G12C)")
    ap.add_argument("--smi", required=True, help="Input .smi file")
    ap.add_argument("--out", required=True, help="Output CSV file")
    
    args = ap.parse_args()

    # 1. Initialize Engine (The expensive part, done once)
    print(f"[*] Initializing Universal Gatekeeper for {args.target}...")
    try:
        gk = UniversalGatekeeper()
    except Exception as e:
        print(f"[!] Engine Initialization Failed: {e}")
        sys.exit(1)

    out_fields = [
        "compound_id", "smiles", "status", "confidence", 
        "reason", "volume", "exposure", "hydrophobic_pct"
    ]

    count = 0
    t0 = time()

    # 2. Screening Loop
    print(f"[*] Starting screen on {args.smi}...")
    with open(args.out, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=out_fields)
        writer.writeheader()

        for cid, smiles in parse_smi(args.smi):
            try:
                # --- CONTRACT CALL ---
                result = gk.validate(args.target, smiles)
                # ---------------------

                status = result.get("status", "ERROR")
                reasons = "; ".join(result.get("reasons", []))
                metrics = result.get("metrics", {}) or {}

                row = {
                    "compound_id": cid,
                    "smiles": smiles,
                    "status": status,
                    "confidence": metrics.get("confidence", 0.0),
                    "reason": reasons,
                    "volume": metrics.get("volume", ""),
                    "exposure": metrics.get("exposure", ""),
                    "hydrophobic_pct": metrics.get("hydrophobic_pct", "")
                }
                writer.writerow(row)
                count += 1
                
                if count % 100 == 0:
                    print(f"\r    Processed {count} compounds...", end="", flush=True)

            except Exception as e:
                # Catch-all to prevent one bad molecule killing the batch
                writer.writerow({
                    "compound_id": cid, 
                    "smiles": smiles, 
                    "status": "ERROR", 
                    "reason": str(e)
                })

    duration = time() - t0
    rate = count / duration if duration > 0 else 0
    print(f"\n[+] Complete. {count} compounds in {duration:.2f}s ({rate:.1f} cmp/s).")
    print(f"[+] Results written to {args.out}")

if __name__ == "__main__":
    main()
