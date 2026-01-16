# Asset Dossier: CHAMP-005

## Identity
- **Sequence:** KAWAKKAAAKAEAAKAEAAKYWPTG
- **Length:** 25 aa
- **Architecture:** Helical peptide (AEAAK repeats + YWPTG warhead)

## Verified Metrics
**Source:** structures/champ005/audit.json (SHA256: 8c0e2830...)

| Metric | Value |
|--------|-------|
| Contact Density (ρ) | 199 |
| Minimum Clearance | 1.63 Å |
| Steric Clashes | 7 (at 2.5Å threshold) |
| Target Heavy Atoms | 935 |
| Binder Heavy Atoms | 185 |

**Chai-1 Confidence:**
- Aggregate Score: 0.3632
- PTM: 0.8351
- iPTM: 0.2452

## Geometric Audit Status
**❌ CLASH_VETO** (Tier 1 Failure)

Seven atom pairs below 2.5Å threshold. Minimum distance of 1.63Å indicates
severe steric violations requiring refinement.

## Comparison to TwinRod-v2
- CHAMP-005 (monovalent): ρ = 199, 7 clashes
- TwinRod-v2 (bipodal): ρ = 336, 1 clash
- **Measured avidity ratio: 1.69x** (not 2.7x as claimed)

## Verdict
Successfully generated with correct sequence but fails geometric validation.
The claimed 2.7x avidity gain is falsified (actual: 1.69x).

Both architectures require clash resolution before Tier 2 validation.

## Artifact Provenance
- **File:** structures/champ005/structure.cif
- **SHA256:** 8c0e283004eda5a18f711fc0c3e5e59ea26d49571af1a8516e4136386002e131
- **Generated:** 2026-01-16 (Kaggle Chai-1 v0.6.1)
- **Audited:** 2026-01-16 (standard_physics_audit v1.0)
- **Sequence Match:** ✅ Verified
