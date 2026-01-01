# Control Atlas — System Map (v1.4)

Control Atlas is organized into **six logical layers**, moving from fundamental constraints to operational scale.

---

## 🧱 Layer 1: Foundations (Constraints)
*Defines what is physically and biologically allowed.*

- **Entries:** 
  - `020_candidate_validation`: Physics Gatekeeper (Volume, Hydrophobicity)
  - `037_chemistry_layer`: Chemical Tractability (Polarity, Conformers)
  - `038_biology_layer`: Biological Relevance (Essentiality, Drivers)
  - `006_motif_mining`, `008_surface_analysis`, `011_pocket_dynamics`: Early physics prototypes (Historical)

## 🧠 Layer 2: Generation (Constrained Proposal)
*Proposes candidates within the allowed space.*

- **Entries:**
  - `019_generative_control`: Generative Logic (Molecules)
  - `060_generative_discovery`: Antibody Generator (Biologics) [Planned/In-Progress]
  - `049_atlas_screening`: Synthetic Library Generation

## 🧬 Layer 3: Structure & Folding
*Validates geometry and stability.*

- **Entries:**
  - `028_structure_prediction`: ESMFold Ingress
  - `027_pocket_detection`: fpocket Integration
  - `050_rfaa_physics`: RoseTTAFold All-Atom (Atomic Resolution)
  - `033_afdb_ingress`: AlphaFold DB Proteome Ingress

## ⚖️ Layer 4: Reasoning (Falsification)
*Proves why a hypothesis fails.*

- **Entries:**
  - `043_proof_engine`: Formal Proof Generation
  - `044_knowledge_graph`: Graph Storage (NetworkX)
  - `045_conjecture_system`: Hypothesis Generation from Failures
  - `046_formalization_bridge`: Logic Translation (Lean-ready)

## 🔁 Layer 5: Loops & Viability
*Closes the epistemic loop.*

- **Entries:**
  - `047_viability_calculus`: The Unified Equation
  - `048_cybernetic_loop`: Axiom Crystallization
  - `040_unified_navigator`: Cross-Layer Integration
  - `029_end_to_end`: Pipeline Orchestration

## 🛠️ Layer 6: Operations (Scale)
*Runs the system in the real world.*

- **Entries:**
  - `024_deployment`: Dockerization
  - `049_atlas_screening`: Batch Production Scripts
  - `051_gpu_orchestration`: Spot Instance Management
  - `052_kaggle_adapter`: Free Compute Persistence
  - `042_knowledge_updater`: Continuous Data Refresh

---

## How to Read This Repo
- **Core Engine:** 040 (Navigator) calls Layers 1, 3, 4.
- **Data Asset:** 034 (Kinome Atlas) is the primary dataset.
- **Theory:** 047 (Calculus) explains the math.
