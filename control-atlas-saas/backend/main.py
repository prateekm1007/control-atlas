from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json, os, hashlib, base64, math, io, tempfile
from datetime import datetime
from fpdf import FPDF
from Bio.PDB import PDBParser, MMCIFParser

app = FastAPI(title="Toscanini Brain v10.0.5")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

NKG_PATH = "/app/nkg/piu_moat.jsonl"
DOCTRINE_VERSION = "v10.0.5-Standard"
SCHEMA_VERSION = "nkg-schema@1.0"

def get_piu_hash(a, b, d):
    pair = sorted([f"{a['res_name']}:{a['atom']}", f"{b['res_name']}:{b['atom']}"])
    raw = f"{pair[0]}_{pair[1]}_{round(d, 1)}"
    motif_tag = f"PIU-155-{pair[0].split(':')[0]}-{pair[1].split(':')[0]}-{round(d, 1)}A"
    return hashlib.md5(raw.encode()).hexdigest()[:12], pair, motif_tag

def get_canonical_snapshot():
    piu_list = []
    if os.path.exists(NKG_PATH):
        with open(NKG_PATH, "r") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if r.get("piu_id") and r["piu_id"] != "HEURISTIC":
                        piu_list.append(r["piu_id"])
                except: continue
    piu_list = sorted(list(set(piu_list)))
    snapshot_obj = {"doctrine": DOCTRINE_VERSION, "pius": piu_list}
    canonical_json = json.dumps(snapshot_obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode()).hexdigest(), len(piu_list)

def generate_v10_certificate(sig, verdict, score, gen, failure_class, nkg_summary, motif_id, details):
    pdf = FPDF()
    snap_hash, total_pius = get_canonical_snapshot()
    
    # --- PAGE 1: EXECUTIVE DECISION ---
    pdf.add_page()
    pdf.set_auto_page_break(False) # PRECISION: Turn off auto-breaks for layout control
    pdf.set_fill_color(10, 15, 30); pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_font("helvetica", "B", 18)
    pdf.cell(0, 15, "FORENSIC DECISION & COMPUTE AVOIDANCE CERTIFICATE", ln=True)
    pdf.set_font("helvetica", "", 9)
    pdf.cell(0, 5, f"Protocol: {DOCTRINE_VERSION} | Signature: {sig}", ln=True)
    pdf.cell(0, 5, f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC", ln=True)
    pdf.ln(8)

    # Verdict Box
    pdf.set_fill_color(30, 41, 59); pdf.rect(10, pdf.get_y(), 190, 25, 'F')
    pdf.set_xy(15, pdf.get_y() + 4); pdf.set_font("helvetica", "B", 14)
    if verdict == "VETO":
        pdf.set_text_color(239, 68, 68); pdf.cell(0, 10, f"FINAL DECISION: {verdict}", ln=True)
    else:
        pdf.set_text_color(16, 185, 129); pdf.cell(0, 10, f"FINAL DECISION: {verdict}", ln=True)
    pdf.set_text_color(220, 220, 220); pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 6, f"Sovereignty Score: {score}% | Class: {failure_class}", ln=True)
    pdf.ln(12)

    # NKG Panel
    pdf.set_text_color(255, 255, 255); pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "NEGATIVE KNOWLEDGE GRAPH STATUS", ln=True)
    pdf.set_draw_color(100, 100, 100); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(4)
    pdf.set_font("helvetica", "B", 10); pdf.set_text_color(251, 191, 36)
    pdf.cell(0, 6, f"Failure Motif ID: {motif_id}", ln=True)
    pdf.set_font("helvetica", "", 9); pdf.set_text_color(200, 200, 200)
    pdf.multi_cell(0, 5, "Motif IDs are geometry-derived and invariant to sequence length or generator seed. The same ID indicates the same physical failure.")
    pdf.ln(2); pdf.set_text_color(230, 230, 230)
    occurrence_text = f"First discovery of this motif." if nkg_summary.get("gen_fails", 0) <= 1 else f"Observed {nkg_summary['gen_fails']} prior instances in local NKG."
    pdf.cell(0, 6, f"NKG Intelligence: {occurrence_text}", ln=True)
    pdf.ln(4); pdf.set_font("helvetica", "B", 10); pdf.set_text_color(255, 255, 255); pdf.cell(0, 6, "Institutional Directive:", ln=True)
    pdf.set_font("helvetica", "I", 10); pdf.multi_cell(0, 5, f"Designs matching {motif_id} should not be resampled with {gen} without explicit structural redesign.")
    pdf.ln(8)

    # Time Avoidance
    pdf.set_font("helvetica", "B", 12); pdf.cell(0, 8, "TIME AVOIDANCE IMPACT", ln=True)
    pdf.set_fill_color(20, 30, 50); pdf.rect(10, pdf.get_y(), 190, 25, 'F')
    pdf.set_xy(15, pdf.get_y() + 4); pdf.set_font("helvetica", "", 9)
    pdf.multi_cell(180, 5, f"- Avoided: Repeated resampling of known-invalid design with {gen}.\n- Typical Impact: One full design iteration cycle (order-of-days to weeks).")
    
    # Force Page 1 Footer
    pdf.set_xy(10, 280)
    pdf.set_font("helvetica", "I", 8); pdf.set_text_color(150, 150, 150)
    pdf.cell(190, 10, "See Page 2 for Technical Annex and Determinism Guarantee", align='C')

    # --- PAGE 2: TECHNICAL ANNEX ---
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=15) # Re-enable for annex
    pdf.set_fill_color(255, 255, 255); pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(0, 0, 0); pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 15, "TECHNICAL ANNEX - NKG STATE & TRACEABILITY", ln=True)
    pdf.ln(2); pdf.set_draw_color(0, 0, 0); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(8)
    
    pdf.set_font("courier", "B", 11); pdf.cell(0, 8, "NKG SNAPSHOT HASH (SHA-256)", ln=True)
    pdf.set_font("courier", "", 9); pdf.multi_cell(0, 5, snap_hash)
    pdf.ln(6)
    
    pdf.set_font("helvetica", "B", 11); pdf.cell(0, 8, "SNAPSHOT IDENTITY & SCOPE", ln=True)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 6, f"- Doctrine Version: {DOCTRINE_VERSION}", ln=True)
    pdf.cell(0, 6, f"- Schema Version: {SCHEMA_VERSION}", ln=True)
    pdf.cell(0, 6, f"- Total Invariant PIUs in Snapshot: {total_pius}", ln=True)
    pdf.cell(0, 6, f"- Law Scope: LAW-155 (Invariant), LAW-162 (Heuristic)", ln=True)
    pdf.ln(6)

    pdf.set_font("helvetica", "B", 11); pdf.cell(0, 8, "DETERMINISM GUARANTEE", ln=True)
    pdf.set_font("helvetica", "", 10)
    pdf.multi_cell(0, 5, "Re-evaluating this structure against the snapshot hash above MUST reproduce the same verdict, independent of operator or execution environment.")
    
    pdf.set_y(260); pdf.set_font("helvetica", "B", 11); pdf.cell(0, 8, "GOVERNANCE SCOPE", ln=True)
    pdf.set_font("helvetica", "", 9); pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, "This certificate is an internal decision-support artifact. It justifies design rejection, generator switching, or pre-sampling constraint enforcement.")
    
    return pdf.output()

def get_atoms(pdb_string, file_ext):
    with tempfile.NamedTemporaryFile(suffix=f".{file_ext}", mode='w', delete=False) as tf:
        tf.write(pdb_string); temp_path = tf.name
    try:
        parser = PDBParser(QUIET=True, PERMISSIVE=1) if file_ext == "pdb" else MMCIFParser(QUIET=True)
        structure = parser.get_structure("AUDIT", temp_path)
        return [{"res_name": r.get_resname(), "res_seq": r.get_id()[1], "chain": c.id, "atom": a.get_name(), 
                 "pos": tuple(float(x) for x in a.get_coord()), "element": a.element}
                for m in structure for c in m for r in c for a in r if a.element != "H"]
    except: return []
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

@app.post("/api/v1/audit/upload")
async def audit_upload(file: UploadFile = File(...), generator: str = Form("Unknown")):
    sig, ext = "UNKNOWN", file.filename.split(".")[-1].lower()
    try:
        content = await file.read(); pdb_string = content.decode("utf-8", errors="replace")
        sig = hashlib.sha256(content).hexdigest()[:16]
        atoms = get_atoms(pdb_string, ext)
        if not atoms: raise ValueError("Unparseable structure")

        # 1. IMMUNITY
        piu_lib = set()
        if os.path.exists(NKG_PATH):
            with open(NKG_PATH, "r") as f:
                for l in f:
                    try: piu_lib.add(json.loads(l)["piu_id"])
                    except: continue
        
        is_imm, m_tag = False, "NONE"
        for i in range(len(atoms)):
            for j in range(i+1, min(i+40, len(atoms))):
                d = math.dist(atoms[i]["pos"], atoms[j]["pos"])
                if d < 2.5:
                    pid, _, mt = get_piu_hash(atoms[i], atoms[j], d)
                    if pid in piu_lib: is_imm, m_tag = True, mt; break

        # 2. PHYSICS
        min_d, culprit = 999.0, None
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                a, b = atoms[i], atoms[j]
                if a["chain"] == b["chain"] and abs(a["res_seq"] - b["res_seq"]) <= 1: continue
                d = math.dist(a["pos"], b["pos"])
                if d < min_d: min_d, culprit = d, (a, b)
        
        # 3. CHEMISTRY
        h_cnt = 0
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                a, b = atoms[i], atoms[j]
                if a["chain"] != b["chain"] and a["element"] in ["N","O"] and b["element"] in ["N","O"]:
                    if math.dist(a["pos"], b["pos"]) <= 3.5: h_cnt += 1
        
        l155_v = min_d < 2.5
        l162_s = "PASS" if h_cnt >= 3 else ("WARNING" if h_cnt > 0 else "VETO")
        verdict = "VETO" if (l155_v or l162_s == "VETO" or is_imm) else "PASS"
        score = int(70 + 30 * min(1.0, (min_d - 2.5))) if verdict == "PASS" else 20
        
        f_class = "IMMUNE MATCH" if is_imm else ("INVARIANT PHYSICAL" if l155_v else "HEURISTIC CHEMICAL")
        nkg_sum = {"is_immune_match": is_imm, "gen_fails": 0}
        if os.path.exists(NKG_PATH):
            with open(NKG_PATH, "r") as f:
                for line in f:
                    if generator in line: nkg_sum["gen_fails"] += 1

        motif_id = get_piu_hash(culprit[0], culprit[1], min_d)[2] if culprit else m_tag
        
        # Ingestion
        if l155_v and culprit and not is_imm:
            p_id, comps, _ = get_piu_hash(culprit[0], culprit[1], min_d)
            with open(NKG_PATH, "a") as f:
                f.write(json.dumps({"piu_id": p_id, "generator": generator, "law_id": "LAW-155", "components": comps, "count": 1, "ts": datetime.utcnow().isoformat()}) + "\n")

        pdf_b = generate_v10_certificate(sig, verdict, score, generator, f_class, nkg_sum, motif_id, "Audit Result")

        return {
            "verdict": verdict, "score": score, "sig": sig, "ext": ext, "mode": "REFUSAL_VETO" if is_imm else "STANDARD",
            "pdb_b64": base64.b64encode(pdb_string.encode()).decode(), "pdf_b64": base64.b64encode(pdf_b).decode(),
            "laws": [{"law_id": "LAW-155", "status": "VETO" if l155_v else "PASS", "measurement": f"{min_d:.2f}", "units": "A", "anchor": tuple((ax+bx)/2 for ax,bx in zip(culprit[0]['pos'], culprit[1]['pos'])) if culprit else None}]
        }
    except Exception as e:
        return {"verdict": "ERROR", "details": str(e), "laws": []}

@app.get("/api/v1/nkg/stats")
def get_nkg_stats():
    if not os.path.exists(NKG_PATH): return {"unique_pius": 0, "model_fingerprints": {}}
    with open(NKG_PATH, "r") as f: records = [json.loads(l) for l in f]
    model_counts = {}
    for r in records: model_counts[r["generator"]] = model_counts.get(r["generator"], 0) + 1
    return {"unique_pius": len(set(r["piu_id"] for r in records)), "model_fingerprints": model_counts}
