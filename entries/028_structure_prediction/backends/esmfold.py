"""
ESMFold API Backend
"""

import requests

ESMFOLD_API_URL = "https://api.esmatlas.com/foldSequence/v1/pdb/"

def predict_structure(sequence: str, timeout: int = 120) -> dict:
    sequence = sequence.upper().strip()
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")

    if not sequence or not all(a in valid_aa for a in sequence):
        return {
            "status": "ERROR",
            "pdb_string": None,
            "confidence_global": 0.0,
            "confidence_per_residue": [],
            "error": "Invalid amino acid sequence"
        }

    if len(sequence) < 10 or len(sequence) > 400:
        return {
            "status": "ERROR",
            "pdb_string": None,
            "confidence_global": 0.0,
            "confidence_per_residue": [],
            "error": "Sequence length outside API limits (10–400)"
        }

    try:
        r = requests.post(
            ESMFOLD_API_URL,
            data=sequence,
            headers={"Content-Type": "text/plain"},
            timeout=timeout
        )

        if r.status_code != 200 or not r.text.strip().startswith("ATOM"):
            return {
                "status": "ERROR",
                "pdb_string": None,
                "confidence_global": 0.0,
                "confidence_per_residue": [],
                "error": f"Invalid response from ESMFold (status={r.status_code})"
            }

        pdb = r.text
        plddt = []

        for line in pdb.splitlines():
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                try:
                    plddt.append(float(line[60:66]) / 100.0)
                except ValueError:
                    pass

        if not plddt:
            return {
                "status": "ERROR",
                "pdb_string": None,
                "confidence_global": 0.0,
                "confidence_per_residue": [],
                "error": "No pLDDT values parsed from structure"
            }

        return {
            "status": "SUCCESS",
            "pdb_string": pdb,
            "confidence_global": round(sum(plddt) / len(plddt), 3),
            "confidence_per_residue": plddt,
            "error": None
        }

    except requests.RequestException as e:
        return {
            "status": "ERROR",
            "pdb_string": None,
            "confidence_global": 0.0,
            "confidence_per_residue": [],
            "error": str(e)
        }
