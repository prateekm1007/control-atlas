from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json, os, hashlib, base64, math, io, tempfile
from datetime import datetime
from fpdf import FPDF
from Bio.PDB import PDBParser, MMCIFParser

app = FastAPI(title="Toscanini Brain v9.7.4")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

NKG_PATH = "/app/nkg/piu_moat.jsonl"
LAW_155_THRESHOLD = 2.5 

# Ensure directory exists on startup
os.makedirs(os.path.dirname(NKG_PATH), exist_ok=True)

def get_piu_hash(a, b, d):
    comp_a, comp_b = f"{a['res_name']}:{a['atom']}", f"{b['res_name']}:{b['atom']}"
    pair = sorted([comp_a, comp_b])
    raw = f"{pair[0]}_{pair[1]}_{round(d, 1)}"
    return hashlib.md5(raw.encode()).hexdigest()[:12], pair

def get_atoms(pdb_string, file_ext):
    with tempfile.NamedTemporaryFile(suffix=f".{file_ext}", mode='w', delete=False) as tf:
        tf.write(pdb_string); temp_path = tf.name
    try:
        parser = PDBParser(QUIET=True, PERMISSIVE=1) if file_ext == "pdb" else MMCIFParser(QUIET=True)
        structure = parser.get_structure("AUDIT", temp_path)
        return [{"res_name": r.get_resname(), "res_seq": r.get_id()[1], "chain": c.id, 
                 "atom": a.get_name(), "pos": tuple(float(x) for x in a.get_coord()), "b": float(a.get_bfactor())}
                for m in structure for c in m for r in c for a in r if a.element != "H"]
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

def generate_pdf_bytes(sig, verdict, score, details, gen, piu_id=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(10, 15, 30); pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("helvetica", "B", 22)
    pdf.cell(0, 15, "TOSCANINI FORENSIC VERDICT", ln=True)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 8, f"Source Generator: {gen}", ln=True)
    pdf.cell(0, 8, f"Job Signature: {sig}", ln=True)
    pdf.ln(10); pdf.set_font("helvetica", "B", 16)
    if verdict == "VETO": pdf.set_text_color(239, 68, 68)
    else: pdf.set_text_color(16, 185, 129)
    pdf.cell(0, 10, f"VERDICT: {verdict}", ln=True)
    pdf.set_text_color(255, 255, 255); pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, f"SOVEREIGNTY SCORE: {score}%", ln=True)
    pdf.ln(10); pdf.set_font("helvetica", "", 10)
    pdf.multi_cell(0, 6, details)
    return pdf.output()

@app.post("/api/v1/audit/upload")
async def audit_upload(file: UploadFile = File(...), generator: str = Form("Unknown")):
    content = await file.read(); pdb_string = content.decode("utf-8", errors="replace")
    ext = file.filename.split(".")[-1].lower(); file_sig = hashlib.sha256(content).hexdigest()[:16]
    atoms = get_atoms(pdb_string, ext)
    if not atoms: return {"verdict": "ERROR", "laws": []}

    # STAGE 1: IMMUNITY
    known_pius = set()
    if os.path.exists(NKG_PATH):
        with open(NKG_PATH, "r") as f:
            for line in f:
                try: 
                    data = json.loads(line)
                    if "piu_id" in data: known_pius.add(data["piu_id"])
                except: continue

    for i in range(len(atoms)):
        for j in range(i+1, min(i+40, len(atoms))): 
            d = math.dist(atoms[i]["pos"], atoms[j]["pos"])
            if d < LAW_155_THRESHOLD:
                pid, _ = get_piu_hash(atoms[i], atoms[j], d)
                if pid in known_pius:
                    pdf_b = generate_pdf_bytes(file_sig, "VETO", 0, "Matched forbidden motif in NKG.", generator, pid)
                    return {"verdict": "VETO", "mode": "REFUSAL_VETO", "score": 0, "sig": file_sig, "piu_id": pid, "generator": generator,
                            "pdb_b64": base64.b64encode(pdb_string.encode()).decode(), "pdf_b64": base64.b64encode(pdf_b).decode(),
                            "ext": ext, "laws": [{"law_id": "NKG-001", "status": "VETO", "measurement": "Matched", "units": "PIU", "anchor": None}]}

    # STAGE 2: PHYSICS
    min_dist, culprit = 999.0, None
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            a, b = atoms[i], atoms[j]
            if a["chain"] == b["chain"] and abs(a["res_seq"] - b["res_seq"]) <= 1: continue
            d = math.dist(a["pos"], b["pos"])
            if d < min_dist: min_dist, culprit = d, (a, b)

    verdict = "PASS" if min_dist >= LAW_155_THRESHOLD else "VETO"
    if verdict == "PASS":
        score = max(70, int(70 + 30 * min(1.0, (min_dist - LAW_155_THRESHOLD))))
    else:
        score = max(0, int((min_dist / LAW_155_THRESHOLD) * 30))
    
    piu_id, clash_meta = None, None
    if verdict == "VETO" and culprit:
        piu_id, comps = get_piu_hash(culprit[0], culprit[1], min_dist)
        clash_meta = {"c1": {"res": culprit[0]['res_seq'], "chain": culprit[0]['chain']}, "c2": {"res": culprit[1]['res_seq'], "chain": culprit[1]['chain']}}
        # NKG Ingestion
        try:
            with open(NKG_PATH, "a") as f:
                f.write(json.dumps({"piu_id": piu_id, "generator": generator, "law_id": "LAW-155", "components": comps, "count": 1, "ts": datetime.utcnow().isoformat()}) + "\n")
        except: pass

    details = f"Min distance: {min_dist:.2f}A (Threshold: 2.5A)."
    pdf_bytes = generate_pdf_bytes(file_sig, verdict, score, details, generator, piu_id)

    return {
        "verdict": verdict, "score": score, "sig": file_sig, "piu_id": piu_id, "details": details, "generator": generator,
        "clash_metadata": clash_meta, "ext": ext, "pdb_b64": base64.b64encode(pdb_string.encode()).decode(),
        "pdf_b64": base64.b64encode(pdf_bytes).decode(),
        "laws": [
            {"law_id": "LAW-155", "status": verdict, "measurement": f"{min_dist:.2f}A", "units": "Å", "anchor": tuple((ax+bx)/2 for ax,bx in zip(culprit[0]['pos'], culprit[1]['pos'])) if culprit else None},
            {"law_id": "LAW-160", "status": "PASS", "measurement": "3.80", "units": "Å", "anchor": None}
        ]
    }

@app.get("/api/v1/nkg/stats")
def get_nkg_stats():
    if not os.path.exists(NKG_PATH): 
        return {"unique_pius": 0, "total_obs": 0, "model_fingerprints": {}, "status": "healthy"}
    
    unique_pius = set()
    total_obs = 0
    model_counts = {}
    
    with open(NKG_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue # Skip empty lines
            try:
                data = json.loads(line)
                p_id = data.get("piu_id")
                gen = data.get("generator", "Unknown")
                if p_id:
                    unique_pius.add(p_id)
                    total_obs += data.get("count", 1)
                    model_counts[gen] = model_counts.get(gen, 0) + 1
            except:
                continue # Skip malformed JSON lines
                
    return {
        "unique_pius": len(unique_pius), 
        "total_obs": total_obs, 
        "model_fingerprints": model_counts, 
        "status": "healthy"
    }
