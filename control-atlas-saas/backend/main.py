from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json, os, hashlib, base64, math, io, tempfile
from datetime import datetime
from fpdf import FPDF
from Bio.PDB import PDBParser, MMCIFParser

app = FastAPI(title="Toscanini Brain v9.4.7")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

NKG_PATH = "/app/nkg/failures.jsonl"
MDI_CODEX = {
    "LAW-001": "Format Protocol: Ensures industrial mmCIF/PDB standards.",
    "LAW-155": "Steric Clash: Non-bonded heavy atoms overlapping (< 1.8Å). Physically impossible.",
    "LAW-170": "pI Balance: Predicts if the protein will aggregate into sludge."
}

def generate_pdf_bytes(sig, verdict, score, details):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(10, 15, 30)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(255, 255, 255)
    
    # UNICODE SAFE: Removed TM symbol to prevent font errors
    pdf.set_font("helvetica", "B", 22)
    pdf.cell(0, 15, "TOSCANINI FORENSIC VERDICT", ln=True, align='L')
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 8, "Industrial Molecular Falsification Instrument", ln=True, align='L')
    pdf.ln(5)
    pdf.set_font("helvetica", "", 9)
    pdf.cell(0, 5, f"Job Signature: {sig}", ln=True)
    pdf.cell(0, 5, f"Timestamp: {datetime.utcnow().isoformat()} UTC", ln=True)
    pdf.ln(10)
    
    pdf.set_font("helvetica", "B", 16)
    if verdict == "VETO":
        pdf.set_text_color(239, 68, 68)
        pdf.cell(0, 10, f"VERDICT: {verdict} - Physical Impossibility Detected", ln=True)
    else:
        pdf.set_text_color(16, 185, 129)
        pdf.cell(0, 10, f"VERDICT: {verdict} - Sovereignty Verified", ln=True)
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, f"SOVEREIGNTY SCORE: {score}%", ln=True)
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "FORENSIC FINDINGS", ln=True)
    pdf.set_font("helvetica", "", 10)
    pdf.multi_cell(0, 6, details)
    return pdf.output()

def get_atoms(pdb_string, file_ext):
    with tempfile.NamedTemporaryFile(suffix=f".{file_ext}", mode='w', delete=False) as tf:
        tf.write(pdb_string)
        temp_path = tf.name
    try:
        parser = PDBParser(QUIET=True, PERMISSIVE=1) if file_ext == "pdb" else MMCIFParser(QUIET=True)
        structure = parser.get_structure("AUDIT", temp_path)
        atom_list = []
        for model in structure:
            for chain in model:
                for residue in chain:
                    res_id = residue.get_id()
                    for atom in residue:
                        if atom.element == "H": continue
                        atom_list.append({
                            "res_name": residue.get_resname(), "res_seq": res_id[1], "chain": chain.id,
                            "atom_name": atom.get_name(), "pos": tuple(float(c) for c in atom.get_coord())
                        })
        return atom_list
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

@app.post("/api/v1/audit/upload")
async def audit_upload(file: UploadFile = File(...)):
    sig = "UNKNOWN"
    ext = file.filename.split(".")[-1].lower()
    try:
        content = await file.read()
        # Secure decoding
        pdb_string = content.decode("utf-8", errors="replace")
        sig = hashlib.sha256(content).hexdigest()[:16]
        
        atoms = get_atoms(pdb_string, ext)
        if not atoms: raise ValueError("Structure empty or malformed. Law-001 Failure.")
            
        min_dist = 999.0
        culprit = None
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                a, b = atoms[i], atoms[j]
                if a["chain"] == b["chain"] and abs(a["res_seq"] - b["res_seq"]) <= 1: continue
                d = math.dist(a["pos"], b["pos"])
                if d < min_dist: min_dist, culprit = d, (a, b)

        verdict = "PASS" if min_dist >= 1.8 else "VETO"
        score = 100 if verdict == "PASS" else max(10, int((min_dist / 2.5) * 100))
        details = f"Min non-bonded distance: {min_dist:.2f}Å."
        clash_metadata = None
        if culprit:
            c1, c2 = culprit
            details += f" Clash: {c1['res_name']}{c1['res_seq']}:{c1['chain']} vs {c2['res_name']}{c2['res_seq']}:{c2['chain']}."
            clash_metadata = {"c1": {"res": c1['res_seq'], "chain": c1['chain']}, "c2": {"res": c2['res_seq'], "chain": c2['chain']}}

        pdf_bytes = generate_pdf_bytes(sig, verdict, score, details)

        if verdict == "VETO":
            os.makedirs(os.path.dirname(NKG_PATH), exist_ok=True)
            if not os.path.exists(NKG_PATH) or sig not in open(NKG_PATH).read():
                with open(NKG_PATH, "a") as f:
                    f.write(json.dumps({"sig": sig, "law": "LAW-155", "ts": datetime.utcnow().isoformat()}) + "\n")

        return {
            "verdict": verdict, "score": score, "sig": sig, "details": details, "ext": ext,
            "clash_metadata": clash_metadata, "pdb_b64": base64.b64encode(pdb_string.encode()).decode(),
            "pdf_b64": base64.b64encode(pdf_bytes).decode(),
            "laws": [
                {"id": "LAW-001", "name": "Format Protocol", "status": "passed", "note": MDI_CODEX["LAW-001"]},
                {"id": "LAW-155", "name": "Steric Clash", "status": "passed" if verdict == "PASS" else "vetoed", "note": MDI_CODEX["LAW-155"]}
            ]
        }
    except Exception as e:
        return {
            "verdict": "ERROR", "score": 0, "sig": sig, "details": f"Forensic Failure: {str(e)}", "ext": ext,
            "clash_metadata": None, "pdb_b64": None, "pdf_b64": None,
            "laws": [{"id": "LAW-001", "name": "Format Protocol", "status": "vetoed", "note": f"Error: {str(e)}"}]
        }

@app.get("/api/v1/nkg/stats")
def get_nkg_stats():
    count = sum(1 for _ in open(NKG_PATH)) if os.path.exists(NKG_PATH) else 0
    return {"total_vetoes": count}
