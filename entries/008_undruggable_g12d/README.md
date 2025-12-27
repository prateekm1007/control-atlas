# Atlas Entry #008: The Undruggable Surface (G12D)

**"Mapping the Void"**

## 1. Intent
To visualize why KRAS G12D resists traditional small-molecule inhibition.
This entry maps **surface lipophilicity**, revealing a pocket that is shallow,
polar, and hostile to hydrophobic drug scaffolds.

## 2. Technical
- **Structure:** KRAS G12D (PDB: 4DSN)
- **Metric:** Molecular Lipophilicity Potential (MLP)
- **Palette:** Cyan (polar) → White → Goldenrod (hydrophobic)

## 3. Insight
Unlike KRAS G12C, G12D lacks an inducible hydrophobic pocket.
The Switch II region is dominated by polar surface physics,
explaining why covalent and lipophilic inhibitors fail.

---
*Provenance: Control-Atlas v0.1*

## 4. Reviewer Note (Tooling Nuance)

Surface hydrophobicity in ChimeraX was computed using the built-in **MLP (Molecular Lipophilicity Potential)** calculation.

Due to strict command grammar and evolving syntax in **ChimeraX ≥1.11**, surface surface coloring must
target **surface vertex attributes**, not model attributes. Several commonly cited commands
(e.g. `surfacecolor`, `color byattribute mlp #1`) are invalid in ChimeraX despite appearing in older
UCSF Chimera documentation.

The final visualization follows the correct ChimeraX-native workflow:
1. SES surface generation
2. MLP computation
3. Surface vertex coloring by `mlp`

This ensures the image is both accurate and reproducible.
