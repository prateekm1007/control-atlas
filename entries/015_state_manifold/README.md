# Entry #015 — Control Pocket State Manifold

## Prerequisite
Entry 016 LOCKED (Physics Gate)

## Objective
Model the constrained deformation manifold of physics-validated control pockets.

## Core Question
What deformations are allowed between closed, intermediate, and open control states?

## Input States
- 5P21 — Native closed (H-Ras)
- 6GOD — GTP-bound intermediate
- 6OIM — Drug-bound open (AMG-510)

## Alignment Frame
G-domain core (exclude Switch I / II)

## Metrics
- Pocket volume
- Concavity index
- SASA (Switch II)
- Pocket centroid displacement

## Method
1. Align cores
2. Extract pocket metrics
3. Compute PCA / distance matrix
4. Visualize low-dimensional manifold

## Success Criteria
- Continuous closed → open trajectory
- Drug-bound state occupies distinct region
- Manifold explains mutant selectivity

## Abort Condition
If states overlap → pocket definition invalid

## Status
[ ] Structures loaded
[ ] Alignment complete
[ ] Metrics extracted
[ ] Manifold computed
[ ] Visualization rendered
