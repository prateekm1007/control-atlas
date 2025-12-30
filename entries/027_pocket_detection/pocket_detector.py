#!/usr/bin/env python3
"""
Entry 027 — General Pocket Detection

Detects druggable pockets on any PDB using fpocket,
computes physics metrics, and applies quality gates.
"""

import argparse
import json
from pathlib import Path

from fpocket_runner import run_fpocket
from physics_metrics import compute_physics


class PocketDetector:
    """
    Unified interface for pocket detection and physics validation.
    """
    
    def __init__(self, max_pockets: int = 5):
        self.max_pockets = max_pockets
    
    def detect(self, pdb_path: str, structure_confidence: float = 1.0) -> dict:
        """
        Detect and validate pockets from a PDB file.
        
        Args:
            pdb_path: Path to PDB file
            structure_confidence: pLDDT from structure prediction (0-1)
        
        Returns:
            {
                "status": "SUCCESS" | "ERROR",
                "pdb_path": str,
                "pockets": [...],
                "validated_count": int,
                "error": str | None
            }
        """
        pdb_path = Path(pdb_path).resolve()
        
        # 1. Run fpocket
        print(f"[*] Running fpocket on {pdb_path.name}...")
        fpocket_result = run_fpocket(str(pdb_path))
        
        if fpocket_result["status"] == "ERROR":
            return {
                "status": "ERROR",
                "pdb_path": str(pdb_path),
                "pockets": [],
                "validated_count": 0,
                "error": fpocket_result["error"]
            }
        
        raw_pockets = fpocket_result["pockets"][:self.max_pockets]
        print(f"[*] Found {len(raw_pockets)} pockets, analyzing top {len(raw_pockets)}...")
        
        # 2. Compute physics for each pocket
        validated_pockets = []
        
        for i, pocket in enumerate(raw_pockets, 1):
            physics = compute_physics(pocket, structure_confidence)
            
            validated_pockets.append({
                "pocket_id": pocket["pocket_id"],
                "rank": i,
                "status": physics["status"],
                "druggability_score": pocket["druggability"],
                "volume": physics["volume"],
                "exposure": physics["exposure"],
                "hydrophobic_pct": physics["hydrophobic_pct"],
                "confidence": physics["confidence"],
                "residue_count": physics["residue_count"],
                "residues": pocket["residues"][:20],  # Limit for readability
                "center": [round(c, 2) for c in pocket["center"]],
                "rejection_reasons": physics["rejection_reasons"]
            })
        
        # Count validated
        validated_count = sum(1 for p in validated_pockets if p["status"] == "VALIDATED")
        candidate_count = sum(1 for p in validated_pockets if p["status"] == "CANDIDATE")
        
        print(f"[*] Results: {validated_count} VALIDATED, {candidate_count} CANDIDATE, {len(validated_pockets) - validated_count - candidate_count} REJECTED")
        
        return {
            "status": "SUCCESS",
            "pdb_path": str(pdb_path),
            "pockets": validated_pockets,
            "validated_count": validated_count,
            "error": None
        }


# --- CLI ---
def main():
    parser = argparse.ArgumentParser(description="Pocket Detection (Entry 027)")
    parser.add_argument("--pdb", required=True, help="Path to PDB file")
    parser.add_argument("--confidence", type=float, default=1.0, 
                        help="Structure confidence (pLDDT, 0-1)")
    parser.add_argument("--max-pockets", type=int, default=5,
                        help="Maximum pockets to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    detector = PocketDetector(max_pockets=args.max_pockets)
    result = detector.detect(args.pdb, structure_confidence=args.confidence)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["status"] == "SUCCESS":
            print(f"\n[+] Pocket Detection Complete")
            print(f"    PDB: {result['pdb_path']}")
            print(f"    Validated Pockets: {result['validated_count']}/{len(result['pockets'])}")
            print()
            for p in result["pockets"]:
                status_icon = "✓" if p["status"] == "VALIDATED" else ("?" if p["status"] == "CANDIDATE" else "✗")
                print(f"    [{status_icon}] {p['pocket_id']} | {p['status']}")
                print(f"        Volume: {p['volume']} Å³ | Hydrophobic: {p['hydrophobic_pct']:.0%} | Confidence: {p['confidence']:.2f}")
                if p["rejection_reasons"]:
                    print(f"        Reasons: {', '.join(p['rejection_reasons'])}")
        else:
            print(f"[!] Detection failed: {result['error']}")


if __name__ == "__main__":
    main()
