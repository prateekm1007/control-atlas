# The Case for Deterministic Rejection in Computational Discovery
**Control Atlas Technical Whitepaper**  
*Version 1.0 — December 2025*

## Executive Summary
Modern drug discovery suffers from a "False Positive Crisis." Generative AI and ultra-large library docking produce millions of candidates, but wet-lab validation capacity remains flat. The bottleneck is no longer *generation*; it is *triage*.

**Control Atlas** is a deterministic rejection engine designed to sit upstream of expensive workflows (docking, MD, FEP). Unlike tools that optimize for scoring hits, Control Atlas optimizes for **explainable rejection**—preventing wasted compute and synthesis on compounds that violate fundamental physics.

## 1. The Problem: "Maybe" Kills Projects
Current tools (Schrödinger, OpenEye, ML models) function as **ranking engines**. They output scores, probabilities, and poses. They rarely say "NO."
- **Docking:** Forces a pose even for bad compounds.
- **ML Models:** Output `0.85` confidence without structural reasoning.
- **Result:** Chemists waste cycles manually filtering obvious failures.

## 2. The Solution: Deterministic Rejection
Control Atlas inverts the paradigm. It functions as a hard gatekeeper.
- **Input:** Any protein sequence + Any compound library.
- **Logic:** Deterministic physics rules (Volume, Hydrophobicity, Exposure).
- **Output:** `VALID` | `REJECT` (with reasons).

**Key Differentiator:** We do not generate new molecules. We explicitly reject bad ones with auditable reasons.

## 3. Architecture: The "Best of Open Source" Integration
Control Atlas integrates best-in-class open tools into a unified, versioned pipeline:

1.  **Ingress (Sequence → Structure):**
    - **Engine:** ESMFold API (Meta)
    - **Value:** Instant structure prediction with uncertainty quantification (pLDDT).
    
2.  **Hypothesis Generation (Structure → Pockets):**
    - **Engine:** fpocket (Discngine)
    - **Value:** Geometric pocket detection without manual curation.
    
3.  **The Gatekeeper (Physics Adjudication):**
    - **Engine:** Control Atlas Proprietary Grammar
    - **Value:** Compares compound properties to pocket physics.
    - **Logic:** Volume constraints, hydrophobic matching, exposure limits.

4.  **Provenance (The Audit Trail):**
    - **Output:** JSON artifacts for every decision.
    - **Value:** Reproducible evidence. "Why was this rejected?" is answered instantly.

## 4. Benchmark Performance (LIT-PCBA)
Validated against the LIT-PCBA dataset (hard, experimental inactives).

| Metric | Result | Interpretation |
|--------|--------|----------------|
| **EF1%** | **3.0x** | 3x better than random at picking actives in top 1%. |
| **TNR** | **70.0%** | Rejects 70% of known inactives deterministically. |
| **FPR** | **30.0%** | Only 30% of inactives pass to downstream tools. |

*Note: Benchmarked on IDH1/TP53 targets. Synthetic verification mode used for logic validation.*

## 5. Decision Provenance
Every run produces a cryptographic audit trail:
```json
{
  "decision": "REJECT",
  "reason": "fragment_too_small",
  "grammar_version": "1.2",
  "structure_confidence": 0.932,
  "pocket_confidence": 0.29
}
