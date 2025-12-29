# Entry #015 — Control Pocket State Manifold

## Prerequisite
Entry 016 LOCKED (Physics Gate)

## Objective
Quantify the constrained deformation manifold of physics-validated control pockets.

## Input States
- 4OBE — GDP closed (KRAS)
- 6GOD — GTP intermediate (KRAS)
- 6OIM — Drug-bound open (AMG-510)
- 5P21 — Native reference (H-Ras)

## Metrics
- Spread (pocket openness)
- Max extent (diameter)
- Z-range (vertical opening)
- Compactness proxy

## Status
[ ] Extraction complete
[ ] Manifold separation confirmed

---

## Entry 015a — CLOSED ❌
**Backbone dispersion metrics insufficient**

### Falsified
Backbone Cα spread does not encode control state.

### Confirmed
Control pockets occupy a constrained geometric region.

---

## Entry 015b — ACTIVE ✅
**Pocket-Frame Manifold**

### Objective
Measure how control states reshape pocket physics, not backbone geometry.

### Metrics
1. Exposure (neighbor-based SASA proxy)
2. Pocket volume (convex hull)
3. Hydrophobic surface fraction

### Lock Criteria
- Drug_open shows highest exposure and volume
- GDP_closed shows lowest
- Intermediate states cluster between

### Abort Condition
No separation → pocket definition incorrect
