from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json, os, hashlib, base64, math, io, tempfile
from datetime import datetime
from fpdf import FPDF
from Bio.PDB import PDBParser, MMCIFParser

app = FastAPI(title="Toscanini Brain v9.8.3")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

NKG_PATH = "/app/nkg/piu_moat.jsonl"
LAW_155_THRESHOLD = 2.5 
LAW_162_DIST = 3.5

def get_piu_hash(a, b, d):
    pair = sorted([f"{a['res_name']}:{a['atom']}", f"{b['res_name']}:{b['atom']}"])
    raw = f"{pair[0]}_{pair[1]}_{round(d, 1)}"
    return hashlib.md5(raw.encode()).hexdigest()[:12], pair

def get_atoms(pdb_string, file_ext):
    with tempfile.NamedTemporaryFile(suffix=f".{file_ext}", mode='w', delete=False) as tf:
        tf.write(pdb_string); temp_path = tf.name
    try:
        parser = PDBParser(QUIET=True, PERMISSIVE=1) if file_ext == "pdb" else MMCIFParser(QUIET=True)
        structure = parser.get_structure("AUDIT", temp_path)
        return [{"res_name": r.get_resname(), "res_seq": r.get_id()[1], "chain": c.id, 
                 "atom": a.get_name(), "pos": tuple(float(x) for x in a.get_coord()), "element": a.element}
                for m in structure for c in m for r in c for a in r if a.element != "H"]
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

def generate_pdf_bytes(sig, verdict, score, details, gen, l162_status, piu_id=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(10, 15, 30); pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("helvetica", "B", 22)
    pdf.cell(0, 15, "TOSCANINI FORENSIC VERDICT", ln=True)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 8, f"Source: {gen} | ID: {sig}", ln=True)
    pdf.ln(10); pdf.set_font("helvetica", "B", 16)
    if verdict == "VETO": pdf.set_text_color(239, 68, 68)
    else: pdf.set_text_color(16, 185, 129)
    pdf.cell(0, 10, f"VERDICT: {verdict}", ln=True)
    pdf.set_text_color(255, 255, 255); pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, f"SOVEREIGNTY SCORE: {score}%", ln=True)
    pdf.ln(5); pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 10, f"Chemical Status (LAW-162): {l162_status}", ln=True)
    pdf.ln(5); pdf.set_font("helvetica", "", 10)
    pdf.multi_cell(0, 6, details)
    if piu_id:
        pdf.ln(5); pdf.set_text_color(251, 191, 36); pdf.cell(0, 10, f"IMMUNE MATCH: {piu_id}", ln=True)
    return pdf.output()

@app.post("/api/v1/audit/upload")
async def audit_upload(file: UploadFile = File(...), generator: str = Form("Unknown")):
    content = await file.read(); pdb_string = content.decode("utf-8", errors="replace")
    ext = file.filename.split(".")[-1].lower(); sig = hashlib.sha256(content).hexdigest()[:16]
    atoms = get_atoms(pdb_string, ext)
    if not atoms: return {"verdict": "ERROR", "laws": []}

    # STAGE 1: IMMUNITY (Check Moat)
    known_pius = set()
    if os.path.exists(NKG_PATH):
        with open(NKG_PATH, "r") as f:
            for line in f:
                try: known_pius.add(json.loads(line)["piu_id"])
                except: continue

    for i in range(len(atoms)):
        for j in range(i+1, min(i+40, len(atoms))): 
            d = math.dist(atoms[i]["pos"], atoms[j]["pos"])
            if d < LAW_155_THRESHOLD:
                pid, _ = get_piu_hash(atoms[i], atoms[j], d)
                if pid in known_pius:
                    pdf_b = generate_pdf_bytes(sig, "VETO", 0, "Immune Veto: Known Physical Failure.", generator, "BLOCKED", pid)
                    return {"verdict": "VETO", "mode": "REFUSAL_VETO", "score": 0, "sig": sig, "piu_id": pid, "generator": generator,
                            "pdb_b64": base64.b64encode(pdb_string.encode()).decode(), "pdf_b64": base64.b64encode(pdf_b).decode(),
                            "laws": [{"law_id": "NKG-001", "status": "VETO", "measurement": "Matched PIU"}]}

    # STAGE 2: PHYSICS (LAW-155)
    min_dist, culprit = 999.0, None
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            a, b = atoms[i], atoms[j]
            if a["chain"] == b["chain"] and abs(a["res_seq"] - b["res_seq"]) <= 1: continue
            d = math.dist(a["pos"], b["pos"])
            if d < min_dist: min_dist, culprit = d, (a, b)
    l155_verdict = "PASS" if min_dist >= LAW_155_THRESHOLD else "VETO"

    # STAGE 3: CHEMISTRY (LAW-162 Heuristic)
    h_count, h_anchor = 0, None
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            a, b = atoms[i], atoms[j]
            if a["chain"] != b["chain"] and a["element"] in ["N","O"] and b["element"] in ["N","O"]:
                d = math.dist(a["pos"], b["pos"])
                if d <= LAW_162_DIST:
                    h_count += 1
                    if not h_anchor: h_anchor = tuple((ax+bx)/2 for ax,bx in zip(a['pos'], b['pos']))

    if h_count >= 3: l162_status = "PASS"
    elif h_count > 0: l162_status = "WARNING"
    else: l162_status = "VETO"

    # FINAL VERDICT
    overall_verdict = "VETO" if (l155_verdict == "VETO" or l162_status == "VETO") else "PASS"
    if overall_verdict == "PASS":
        base_score = max(70, int(70 + 30 * min(1.0, (min_dist - LAW_155_THRESHOLD))))
        score = base_score - 15 if l162_status == "WARNING" else base_score
    else:
        score = max(0, min(30, int((min_dist / LAW_155_THRESHOLD) * 30)))

    # NKG PERSISTENCE (PIUs + Telemetry)
    piu_id = None
    if l155_verdict == "VETO" and culprit:
        piu_id, comps = get_piu_hash(culprit[0], culprit[1], min_dist)
        # Record PIU if new for this model
        existing = open(NKG_PATH).read() if os.path.exists(NKG_PATH) else ""
        if f'"{piu_id}"' not in existing or f'"{generator}"' not in existing:
            with open(NKG_PATH, "a") as f:
                f.write(json.dumps({"piu_id": piu_id, "generator": generator, "law_id": "LAW-155", "components": comps, "count": 1, "ts": datetime.utcnow().isoformat()}) + "\n")
    
    # NEW: Log non-PIU failures (like LAW-162) for analytics-only telemetry
    elif l162_status == "VETO":
        with open(NKG_PATH, "a") as f:
            f.write(json.dumps({"piu_id": "HEURISTIC", "generator": generator, "law_id": "LAW-162", "count": 1, "ts": datetime.utcnow().isoformat()}) + "\n")

    details = f"Min non-bonded dist: {min_dist:.2f}A. H-Bond saturation: {h_count}."
    pdf_bytes = generate_pdf_bytes(sig, overall_verdict, score, details, generator, l162_status, piu_id)

    return {
        "verdict": overall_verdict, "score": score, "sig": sig, "ext": ext, "laws": [
            {"law_id": "LAW-155", "status": l155_verdict, "measurement": f"{min_dist:.2f}Å", "anchor": tuple((ax+bx)/2 for ax,bx in zip(culprit[0]['pos'], culprit[1]['pos'])) if culprit else None},
            {"law_id": "LAW-162", "status": l162_status, "measurement": f"{h_count}", "units": "Bonds (Dist-Heuristic)", "anchor": h_anchor}
        ], "pdb_b64": base64.b64encode(pdb_string.encode()).decode(), "pdf_b64": base64.b64encode(pdf_bytes).decode()
    }

@app.get("/api/v1/nkg/stats")
def get_nkg_stats():
    if not os.path.exists(NKG_PATH): return {"unique_pius": 0, "total_obs": 0, "model_fingerprints": {}, "audit_failures": {}}
    with open(NKG_PATH, "r") as f: records = [json.loads(l) for l in f]
    
    unique_ids = len(set(r["piu_id"] for r in records if r["piu_id"] != "HEURISTIC"))
    model_counts = {} # Unique PIUs per generator
    audit_failures = {} # Total failures (PIU + Heuristic)
    
    for r in records:
        g = r.get("generator", "Unknown")
        audit_failures[g] = audit_failures.get(g, 0) + 1
        if r["piu_id"] != "HEURISTIC":
            model_counts[g] = model_counts.get(g, 0) + 1
            
    return {"unique_pius": unique_ids, "total_obs": len(records), "model_fingerprints": model_counts, "audit_failures": audit_failures}
