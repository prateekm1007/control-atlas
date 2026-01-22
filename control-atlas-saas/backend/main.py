from fastapi import FastAPI, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
import json, os, hashlib, base64, math, io, tempfile
from datetime import datetime
from fpdf import FPDF
from Bio.PDB import PDBParser, MMCIFParser
import google.generativeai as genai

app = FastAPI(title="Toscanini Brain v10.3.7")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GEMINI_KEY = os.getenv("GEMINI_API_KEY", "NONE")
NKG_PATH = "/app/nkg/piu_moat.jsonl"
DOCTRINE_VERSION = "v10.3.7-Standard"

LAW_CANON = {
    "LAW-155": {"title": "Steric Clash Prohibition", "conf": "HARD", "principle": "Atoms cannot overlap.", "threshold": "2.5A", "why": "Physical impossibility."},
    "LAW-160": {"title": "Backbone Continuity", "conf": "HARD", "principle": "Fixed C-Alpha spacing.", "threshold": "3.5A - 4.2A", "why": "Polymer integrity failure."},
    "LAW-162": {"title": "Interface Saturation", "conf": "ADVISORY", "principle": "H-Bond handshake.", "threshold": ">= 3 Bonds", "why": "Affinity risk."}
}

def sanitize_for_pdf(text):
    repls = {'’': "'", '‘': "'", '“': '"', '”': '"', '–': "-", '—': "-", '•': "-", 'Å': "A", '\u00a0': " ", '*': ""}
    for char, rep in repls.items():
        text = text.replace(char, rep)
    return text.encode('ascii', 'ignore').decode('ascii')

def get_piu_hash(a, b, d):
    pair = sorted([f"{a['res_name']}:{a['atom']}", f"{b['res_name']}:{b['atom']}"])
    raw = f"{pair[0]}_{pair[1]}_{round(d, 1)}"
    tag = f"PIU-155-{pair[0].split(':')[0]}-{pair[1].split(':')[0]}-{round(d, 1)}A"
    return hashlib.md5(raw.encode()).hexdigest()[:12], pair, tag

def synthesize_apex_rationale(verdict, score, gen, law_results, nkg_count):
    if not GEMINI_KEY: return "Manual review required.", "NO_KEY"
    model_hierarchy = ["deep-research-pro-preview-12-2025", "gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-2.5-pro"]
    genai.configure(api_key=GEMINI_KEY)
    for model_name in model_hierarchy:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = f"Lead Forensic Biologist: Analyze {verdict} ({score}%) for {gen}. Failures: {json.dumps(law_results)}. NKG Matches: {nkg_count}. Write a 2-sentence Causal Rationale on why this design is a 'Biological Hallucination'. Tone: Industrial, Executive. 3 sentences max."
            response = model.generate_content(prompt, request_options={"timeout": 15})
            return sanitize_for_pdf(response.text), f"APEX_{model_name.upper()}"
        except: continue
    return "Causal synthesis offline. Physical violation detected by engine.", "HIERARCHY_FAIL"

def generate_v10_certificate(sig, verdict, score, gen, f_class, m_id, actions, rationale, law_results, nkg_count):
    pdf = FPDF()
    pdf.add_page(); pdf.set_auto_page_break(False)
    pdf.set_fill_color(10, 15, 30); pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("helvetica", "B", 18)
    pdf.cell(0, 15, "FORENSIC DECISION & COMPUTE AVOIDANCE CERTIFICATE", ln=True)
    pdf.set_font("helvetica", "", 9); pdf.cell(0, 5, f"Generator: {gen} | Protocol: {DOCTRINE_VERSION} | Sig: {sig}", ln=True); pdf.ln(10)
    pdf.set_fill_color(30, 41, 59); pdf.rect(10, pdf.get_y(), 190, 25, 'F')
    pdf.set_xy(15, pdf.get_y() + 4); pdf.set_font("helvetica", "B", 14)
    # COLOR FIX
    if verdict == "VETO": pdf.set_text_color(239, 68, 68)
    elif verdict == "WARNING": pdf.set_text_color(251, 191, 36)
    else: pdf.set_text_color(16, 185, 129)
    pdf.cell(0, 8, f"FINAL DECISION: {verdict}", ln=True)
    pdf.set_text_color(200, 200, 200); pdf.set_font("helvetica", "B", 10); pdf.cell(0, 6, f"Score: {score}% | Class: {f_class}", ln=True); pdf.ln(12)
    pdf.set_text_color(255, 255, 255); pdf.set_font("helvetica", "B", 12); pdf.cell(0, 8, "CAUSAL RATIONALE (AI-SYNTHESIZED)", ln=True); pdf.ln(2)
    pdf.set_font("helvetica", "I", 10); pdf.set_text_color(220, 220, 220); pdf.multi_cell(0, 5, rationale); pdf.ln(8)
    pdf.set_font("helvetica", "B", 12); pdf.set_text_color(255, 255, 255); pdf.cell(0, 8, "INSTITUTIONAL DIRECTIVE", ln=True)
    pdf.set_font("helvetica", "", 10); pdf.set_text_color(251, 191, 36); pdf.cell(0, 6, f"Motif ID: {m_id} | NKG Matches: {nkg_count}", ln=True)
    pdf.set_xy(10, 280); pdf.set_font("helvetica", "I", 8); pdf.set_text_color(150, 150, 150); pdf.cell(190, 10, "See Page 2 for Technical Annex", align='C')
    pdf.add_page(); pdf.set_auto_page_break(True, margin=15); pdf.set_fill_color(255, 255, 255); pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(0, 0, 0); pdf.set_font("helvetica", "B", 16); pdf.cell(0, 15, "TECHNICAL ANNEX - NKG STATE", ln=True); pdf.ln(5)
    for l in law_results:
        pdf.set_font("helvetica", "B", 9); pdf.cell(40, 7, l['law_id'], 0); pdf.set_font("helvetica", "", 9); pdf.cell(150, 7, f"Status: {l['status']} | Obs: {l['measurement']}", 0, ln=True)
    return pdf.output()

def get_atoms(pdb_string, file_ext):
    with tempfile.NamedTemporaryFile(suffix=f".{file_ext}", mode='w', delete=False) as tf:
        tf.write(pdb_string); temp_path = tf.name
    try:
        parser = PDBParser(QUIET=True, PERMISSIVE=1) if file_ext == "pdb" else MMCIFParser(QUIET=True)
        structure = parser.get_structure("AUDIT", temp_path)
        return [{"res_name": r.get_resname(), "res_seq": r.get_id()[1], "chain": c.id, "atom": a.get_name(), 
                 "pos": tuple(float(x) for x in a.get_coord()), "element": a.element, "b": float(a.get_bfactor())}
                for m in structure for c in m for r in c for a in r if a.element != "H"]
    except: return []
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

@app.post("/api/v1/audit/upload")
async def audit_upload(file: UploadFile = File(...), generator: str = Form("Unknown")):
    sig, ext = "UNKNOWN", file.filename.split(".")[-1].lower()
    try:
        content = await file.read(); pdb_string = content.decode("utf-8", errors="replace")
        sig = hashlib.sha256(content).hexdigest()[:16]; atoms = get_atoms(pdb_string, ext)
        if not atoms: raise ValueError("Unparseable structure")

        # IMMUNITY
        piu_lib = {json.loads(l)["piu_id"] for l in open(NKG_PATH)} if os.path.exists(NKG_PATH) else set()
        is_imm, m_tag = False, "NONE"
        for i in range(len(atoms)):
            for j in range(i+1, min(i+40, len(atoms))):
                d = math.dist(atoms[i]["pos"], atoms[j]["pos"])
                if d < 2.5:
                    pid, _, mt = get_piu_hash(atoms[i], atoms[j], d); 
                    if pid in piu_lib: is_imm, m_tag = True, mt; break

        # PHYSICS
        min_d, culprit = 999.0, None
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                a, b = atoms[i], atoms[j]
                if a["chain"] == b["chain"] and abs(a["res_seq"] - b["res_seq"]) <= 1: continue
                d = math.dist(a["pos"], b["pos"])
                if d < min_d: min_d, culprit = d, (a, b)
        l155_v = min_d < 2.5
        ca_atoms = [a for a in atoms if a["atom"] == "CA"]
        l160_v = any(math.dist(ca_atoms[i]["pos"], ca_atoms[i+1]["pos"]) > 4.2 for i in range(len(ca_atoms)-1) if ca_atoms[i]["chain"] == ca_atoms[i+1]["chain"])
        h_cnt = sum(1 for i in range(len(atoms)) for j in range(i+1, len(atoms)) 
                    if atoms[i]["chain"] != atoms[j]["chain"] and atoms[i]["element"] in ["N","O"] 
                    and atoms[j]["element"] in ["N","O"] and math.dist(atoms[i]["pos"], atoms[j]["pos"]) <= 3.5)

        # COMPILE
        raw_res = {"LAW-155": {"fail": l155_v, "val": f"{min_d:.2f}A"},
                   "LAW-160": {"fail": l160_v, "val": "Broken" if l160_v else "Pass"},
                   "LAW-162": {"fail": h_cnt == 0, "warn": h_cnt < 3 and h_cnt > 0, "val": f"{h_cnt} Bonds"}}

        if is_imm: verdict, f_class = "VETO", "IMMUNE MATCH"
        elif l155_v or l160_v: verdict, f_class = "VETO", "INVARIANT PHYSICAL"
        elif raw_res["LAW-162"]["fail"] or raw_res["LAW-162"]["warn"]: verdict, f_class = "WARNING", "HEURISTIC CHEMICAL"
        else: verdict, f_class = "PASS", "PRISTINE"

        score = 20 if verdict == "VETO" else (65 if verdict == "WARNING" else 100)
        actions = ["Kill design branch."] if verdict == "VETO" else ["Adjust interface chemistry."]
        m_tag = get_piu_hash(culprit[0], culprit[1], min_d)[2] if culprit else m_tag
        nkg_count = sum(1 for l in open(NKG_PATH) if m_tag in l) if os.path.exists(NKG_PATH) else 0
        
        # FIX: Scope variables correctly to 'r' loop
        law_results = [{"law_id": lid, "status": "VETO" if r["fail"] else ("WARNING" if r.get("warn") else "PASS"), 
                      "conf": LAW_CANON[lid]["conf"], "measurement": r["val"]} for lid, r in raw_res.items()]

        narrative, llm_status = synthesize_apex_rationale(verdict, score, generator, law_results, nkg_count)
        pdf = generate_v10_certificate(sig, verdict, score, generator, f_class, m_tag, actions, narrative, law_results, nkg_count)

        if l155_v and culprit:
            p_id, _, _ = get_piu_hash(culprit[0], culprit[1], min_d)
            with open(NKG_PATH, "a") as f: f.write(json.dumps({"piu_id": p_id, "generator": generator}) + "\n")

        return {
            "verdict": verdict, "score": score, "sig": sig, "ext": ext, "narrative": narrative, "llm_status": llm_status,
            "pdf_b64": base64.b64encode(pdf).decode(), "pdb_b64": base64.b64encode(pdb_string.encode()).decode(),
            "laws": law_results
        }
    except Exception as e: return {"verdict": "ERROR", "details": str(e)}

@app.get("/api/v1/nkg/stats")
def get_nkg_stats():
    if not os.path.exists(NKG_PATH): return {"unique_pius": 0}
    with open(NKG_PATH, "r") as f: records = [json.loads(l) for l in f]
    return {"unique_pius": len(set(r["piu_id"] for r in records)), "model_fingerprints": {r["generator"]: 1 for r in records}}
