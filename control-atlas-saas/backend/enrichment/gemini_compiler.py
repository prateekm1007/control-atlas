import google.generativeai as genai
import os, json

class GeminiCompiler:
    def __init__(self, key):
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def synthesize(self, verdict, score, gen, results):
        # Extract specific failures for the prompt
        failures = [f"{r['law_id']}: {r['measurement']}" for r in results if r['status'] == 'FAIL']
        failure_context = "\n".join(failures) if failures else "No specific invariant violations."

        prompt = f"""
        ROLE: Senior PhD Structural Biologist & Forensic Notary.
        CONTEXT: You are auditing a protein design claim from {gen}.
        VERDICT: {verdict} ({score}% Physical Integrity).
        VIOLATIONS DETECTED: 
        {failure_context}

        TASK: Write a 150-word authoritative technical paragraph.
        
        IF VETOED: 
        - Provide a 'Forensic Autopsy'. 
        - Explain how the specific violations (e.g., the {failure_context}) represent a catastrophic failure of physical reality. 
        - Discuss the 'Van der Waals repulsion' or 'Peptide bond instability' caused by these coordinates.
        - State clearly why this design would aggregate or collapse immediately during synthesis.
        
        IF PASSED: 
        - Explain the 'Thermodynamic Credibility' of the structure.
        - Highlight the lack of steric strain and the consistency of the hydrogen-bond registry.
        
        TERMINOLOGY MANDATE: Use 'Pauli exclusion', 'torsional strain', 'Gibbs free energy', and 'biophysical impossibility'. 
        Avoid bullet points. One dense, professional paragraph.
        """
        try:
            response = self.model.generate_content(prompt)
            # Remove markdown stars and ensure clean text
            text = response.text.replace('*', '').strip()
            return text
        except Exception:
            if verdict == "VETO":
                return f"Forensic VETO: The design is physically impossible due to {failure_context}. " \
                       "Steric overlaps or backbone discontinuities detected represent infinite energy gradients " \
                       "that preclude biological existence."
            return "Structural integrity verified against Tier-1 Physical Invariants."
