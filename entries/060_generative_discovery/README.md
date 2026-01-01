# Entry 060 — Antibody Generator

Generates candidate antibody sequences for a given antigen.

## Methods
- **Framework:** Trastuzumab-like (humanized IgG1)
- **Diversity:** Randomized CDR3 generation (Mock) / PLM Infilling (Prod)
- **Output:** JSON list of Heavy/Light chains

## Usage
```bash
python generate_antibodies.py --target "MTEYKLVVVGAGGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDGETCLLDILDTAGQ" --num 50
