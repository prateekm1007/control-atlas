#!/usr/bin/env python3
"""
Entry 029 — End-to-End Sequence Screening Pipeline

Chain: Sequence → Structure (028) → Pockets (027) → Screening (020) → Results

Single command for any protein sequence + compound library.
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from time import time

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from entries.028_structure_prediction.structure_provider import StructureProvider
from entries.027_pocket_detection.pocket_detector import PocketDetector
from entries.020_candidate_validation.universal_gatekeeper import UniversalGatekeeper


def parse_smi(smi_path):
    """Yield (compound_id, smiles) from .smi file."""
    with open(smi_path, "r") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            smiles = parts[0]
            cid = parts[1] if len(parts) > 1 else f"cmp_{idx+1:06d}"
            yield cid, smiles


def main():
    parser = argparse.ArgumentParser(
        description="End-to-End Sequence Screening (Entry 029)"
    )
    parser.add_argument("--sequence", required=True, help="Amino acid sequence")
    parser.add_argument("--smi", required=True, help="Compound library (.smi)")
    parser.add_argument("--out", required=True, help="Output CSV")
    parser.add_argument("--max-pockets", type=int, default=3, 
                        help="Max pockets to screen against")
    parser.add_argument("--json-trace", help="Optional JSON trace output")
    args = parser.parse_args()

    trace = {
        "sequence_length": len(args.sequence),
        "stages": {}
    }
    
    t0 = time()

    # ============================================================
    # STAGE 1: Structure Prediction (Entry 028)
    # ============================================================
    print("\n" + "="*60)
    print("STAGE 1: Structure Prediction")
    print("="*60)
    
    structure_provider = StructureProvider()
    structure_result = structure_provider.predict(args.sequence)
    
    if structure_result["status"] != "SUCCESS":
        print(f"[!] Structure prediction failed: {structure_result['error']}")
        sys.exit(1)
    
    pdb_path = structure_result["pdb_path"]
    structure_confidence = structure_result["confidence_global"]
    
    print(f"[+] Structure: {pdb_path}")
    print(f"[+] Confidence: {structure_confidence:.1%}")
    
    trace["stages"]["structure"] = {
        "pdb_path": pdb_path,
        "confidence": structure_confidence,
        "cached": structure_result["cached"]
    }

    # ============================================================
    # STAGE 2: Pocket Detection (Entry 027)
    # ============================================================
    print("\n" + "="*60)
    print("STAGE 2: Pocket Detection")
    print("="*60)
    
    pocket_detector = PocketDetector(max_pockets=args.max_pockets)
    pocket_result = pocket_detector.detect(pdb_path, structure_confidence)
    
    if pocket_result["status"] != "SUCCESS":
        print(f"[!] Pocket detection failed: {pocket_result['error']}")
        sys.exit(1)
    
    # Filter to VALIDATED and CANDIDATE pockets only
    screenable_pockets = [
        p for p in pocket_result["pockets"] 
        if p["status"] in ("VALIDATED", "CANDIDATE")
    ]
    
    if not screenable_pockets:
        print("[!] No druggable pockets found. Cannot screen.")
        print("    This protein may lack suitable binding sites.")
        sys.exit(0)
    
    print(f"[+] Screenable pockets: {len(screenable_pockets)}")
    for p in screenable_pockets:
        print(f"    - {p['pocket_id']}: {p['status']} (conf: {p['confidence']:.2f})")
    
    trace["stages"]["pockets"] = {
        "total_detected": len(pocket_result["pockets"]),
        "screenable": len(screenable_pockets),
        "pockets": [
            {
                "id": p["pocket_id"],
                "status": p["status"],
                "confidence": p["confidence"],
                "volume": p["volume"]
            }
            for p in screenable_pockets
        ]
    }

    # ============================================================
    # STAGE 3: Compound Screening (Entry 020)
    # ============================================================
    print("\n" + "="*60)
    print("STAGE 3: Compound Screening")
    print("="*60)
    
    # Build dynamic catalog from detected pockets
    dynamic_catalog = {}
    for p in screenable_pockets:
        target_id = f"SEQ_{p['pocket_id']}"
        dynamic_catalog[target_id] = {
            "status": p["status"],
            "volume": p["volume"],
            "hydrophobic_pct": p["hydrophobic_pct"],
            "exposure": p["exposure"],
            "pocket_confidence": p["confidence"],
            "structure_confidence": structure_confidence
        }
    
    # Initialize gatekeeper with dynamic catalog
    gk = UniversalGatekeeper()
    gk.catalog.update(dynamic_catalog)
    
    compounds = list(parse_smi(args.smi))
    print(f"[*] Screening {len(compounds)} compounds against {len(screenable_pockets)} pockets")
    
    # Output fields
    out_fields = [
        "compound_id", "smiles", "pocket", "status", "confidence",
        "reason", "volume", "hydrophobic_pct", "structure_conf", "pocket_conf"
    ]
    
    results = []
    screen_count = 0
    
    for cid, smiles in compounds:
        for p in screenable_pockets:
            target_id = f"SEQ_{p['pocket_id']}"
            
            try:
                result = gk.validate(target_id, smiles)
                
                status = result.get("status", "ERROR")
                reasons = "; ".join(result.get("reasons", []))
                metrics = result.get("metrics", {}) or {}
                
                # Propagate confidence: structure × pocket × compound match
                compound_conf = metrics.get("confidence", 0.0)
                combined_conf = structure_confidence * p["confidence"] * compound_conf
                
                row = {
                    "compound_id": cid,
                    "smiles": smiles,
                    "pocket": p["pocket_id"],
                    "status": status,
                    "confidence": round(combined_conf, 3),
                    "reason": reasons,
                    "volume": p["volume"],
                    "hydrophobic_pct": p["hydrophobic_pct"],
                    "structure_conf": round(structure_confidence, 3),
                    "pocket_conf": round(p["confidence"], 3)
                }
                results.append(row)
                screen_count += 1
                
            except Exception as e:
                results.append({
                    "compound_id": cid,
                    "smiles": smiles,
                    "pocket": p["pocket_id"],
                    "status": "ERROR",
                    "confidence": 0.0,
                    "reason": str(e)
                })
    
    # Sort by confidence descending
    results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    
    # Write output
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)
    
    dt = time() - t0
    
    print(f"\n[+] Complete: {screen_count} screens in {dt:.2f}s")
    print(f"[+] Output: {args.out}")
    
    # Summary
    valid_count = sum(1 for r in results if r["status"] == "VALID")
    candidate_count = sum(1 for r in results if r["status"] == "CANDIDATE")
    reject_count = sum(1 for r in results if r["status"] == "REJECT")
    
    print(f"\n    VALID: {valid_count}")
    print(f"    CANDIDATE: {candidate_count}")
    print(f"    REJECT: {reject_count}")
    
    # Top hits
    top_hits = [r for r in results if r["status"] in ("VALID", "CANDIDATE")][:5]
    if top_hits:
        print(f"\n    Top Hits:")
        for h in top_hits:
            print(f"      {h['compound_id']} → {h['pocket']} ({h['status']}, conf: {h['confidence']:.3f})")
    
    trace["stages"]["screening"] = {
        "compounds": len(compounds),
        "screens": screen_count,
        "valid": valid_count,
        "candidate": candidate_count,
        "reject": reject_count
    }
    trace["total_time_s"] = round(dt, 2)
    
    # Write trace
    if args.json_trace:
        with open(args.json_trace, "w") as f:
            json.dump(trace, f, indent=2)
        print(f"[+] Trace: {args.json_trace}")


if __name__ == "__main__":
    main()
