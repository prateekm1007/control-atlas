import subprocess
import json
import os

class AdversarialEngine:
    """
    Cross-examines AI designs against clinical gold-standards (e.g., WL12/5NIU).
    Uses alignment_validator.py to calculate interface similarity.
    """
    
    @staticmethod
    def compare_to_reference(design_path: str, target_chain: str, binder_chain: str):
        # Path to the clinical reference receipt
        ref_path = "/app/tools/ref_5NIU.pdb" 
        validator_script = "/app/tools/alignment_validator.py"
        
        if not os.path.exists(ref_path) or not os.path.exists(validator_script):
            return {"error": "Clinical reference data missing", "score": 0}

        try:
            # Command: python alignment_validator.py design.cif ref.pdb --target A --binder B
            cmd = [
                "python3", validator_script,
                design_path,
                ref_path,
                "--target", target_chain,
                "--binder", binder_chain
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Assuming alignment_validator outputs RMSD
            # We convert RMSD to a 'Sovereignty Score' (0-100%)
            # Score = 100 * exp(-RMSD) -- High score = close to clinical reality
            try:
                data = json.loads(result.stdout)
                rmsd = data.get("rmsd", 5.0)
                sovereignty_score = round(max(0, 100 * (2.0 / (2.0 + rmsd))), 2)
                return {
                    "rmsd_vs_clinical": rmsd,
                    "sovereignty_score": sovereignty_score,
                    "status": "VALIDATED" if rmsd < 2.0 else "HALLUCINATION_RISK"
                }
            except:
                return {"rmsd_vs_clinical": 9.99, "sovereignty_score": 0, "status": "ALIGNMENT_FAILURE"}
                
        except Exception as e:
            return {"error": str(e), "sovereignty_score": 0}

    @staticmethod
    def get_clinical_benchmarks():
        """Returns the stats for CHAMP-005 and WL12 to show on the dashboard."""
        return {
            "CHAMP-005": {"rmsd": 0.22, "rho": 147, "status": "CLINICAL_GRADE"},
            "WL12": {"rmsd": 0.00, "rho": 180, "status": "REFERENCE_PDB"}
        }
