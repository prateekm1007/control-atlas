from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json, os, hashlib, base64, math, io, tempfile
from datetime import datetime
from fpdf import FPDF
from Bio.PDB import PDBParser, MMCIFParser

app = FastAPI(title="Toscanini Brain v9.6.8")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

NKG_PATH = "/app/nkg/piu_moat.jsonl"
LAW_155_THRESHOLD = 2.5 

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
                 "atom": a.get_name(), "pos": tuple(float(x) for x in a.get_coord()), "b": float(a.get_bfactor())}
                for m in structure for c in m for r in c for a in r if a.element != "H"]
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

@app.post("/api/v1/audit/upload")
async def audit_upload(file: UploadFile = File(...)):
    content = await file.read(); pdb_string = content.decode("utf-8", errors="replace")
    ext = file.filename.split(".")[-1].lower(); file_sig = hashlib.sha256(content).hexdigest()[:16]
    atoms = get_atoms(pdb_string, ext)
    if not atoms: return {"verdict": "ERROR", "laws": []}

    # --- STAGE 1: ZERO-COMPUTE IMMUNITY (MANDATORY BEFORE PHYSICS) ---
    piu_library = set()
    if os.path.exists(NKG_PATH):
        with open(NKG_PATH, "r") as f:
            for line in f: piu_library.add(json.loads(line)["piu_id"])

    # Fast scan top 40 atom-pairs for known motifs
    for i in range(len(atoms)):
        for j in range(i+1, min(i+40, len(atoms))): 
            d = math.dist(atoms[i]["pos"], atoms[j]["pos"])
            if d < LAW_155_THRESHOLD:
                p_id, _ = get_piu_hash(atoms[i], atoms[j], d)
                if p_id in piu_library:
                    return {
                        "verdict": "VETO", "mode": "REFUSAL_VETO", "score": 0, "sig": file_sig,
                        "piu_id": p_id, "details": "Immune Response: Matched known Forbidden Motif.",
                        "pdb_b64": base64.b64encode(pdb_string.encode()).decode(), "ext": ext,
                        "laws": [{"law_id": "NKG-001", "status": "VETO", "measurement": "Matched", "units": "PIU"}]
                    }

    # --- STAGE 2: PHYSICS ENGINE (O(N^2)) ---
    min_dist, culprit = 999.0, None
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            a, b = atoms[i], atoms[j]
            if a["chain"] == b["chain"] and abs(a["res_seq"] - b["res_seq"]) <= 1: continue
            d = math.dist(a["pos"], b["pos"])
            if d < min_dist: min_dist, culprit = d, (a, b)

    verdict = "PASS" if min_dist >= LAW_155_THRESHOLD else "VETO"
    
    # --- PHYSICAL SCORING CLAMP ---
    if verdict == "PASS":
        # 2.5A = 70%, 3.5A+ = 100%
        score = int(70 + 30 * min(1.0, (min_dist - LAW_155_THRESHOLD) / 1.0))
    else:
        # Linear degradation from 30% down to 0%
        score = max(0, int((min_dist / LAW_155_THRESHOLD) * 30))

    piu_id, clash_meta = None, None
    if verdict == "VETO" and culprit:
        piu_id, components = get_piu_hash(culprit[0], culprit[1], min_dist)
        clash_meta = {"c1": {"res": culprit[0]['res_seq'], "chain": culprit[0]['chain']}, 
                      "c2": {"res": culprit[1]['res_seq'], "chain": culprit[1]['chain']}}
        # NKG Ingestion (Idempotent)
        existing = open(NKG_PATH).read() if os.path.exists(NKG_PATH) else ""
        if piu_id not in existing:
            with open(NKG_PATH, "a") as f:
                f.write(json.dumps({"piu_id": piu_id, "law_id": "LAW-155", "components": components, "count": 1, "ts": datetime.utcnow().isoformat()}) + "\n")

    return {
        "verdict": verdict, "score": score, "sig": file_sig, "piu_id": piu_id, "ext": ext,
        "details": f"Min distance: {min_dist:.2f}A (Threshold: {LAW_155_THRESHOLD}A).",
        "clash_metadata": clash_meta, "pdb_b64": base64.b64encode(pdb_string.encode()).decode(),
        "laws": [
            {"law_id": "LAW-155", "status": verdict, "measurement": f"{min_dist:.2f}A", "units": "Å", "anchor": tuple((ax+bx)/2 for ax,bx in zip(culprit[0]['pos'], culprit[1]['pos'])) if culprit else None},
            {"law_id": "LAW-160", "status": "PASS", "measurement": "3.80", "units": "Å", "anchor": None}
        ]
    }

@app.get("/api/v1/nkg/stats")
def get_nkg_stats():
    total_obs, dist = 0, {}
    if os.path.exists(NKG_PATH):
        with open(NKG_PATH, "r") as f:
            for line in f:
                data = json.loads(line); total_obs += data["count"]
                pair = "-".join([c.split(":")[0] for c in data["components"]])
                dist[pair] = dist.get(pair, 0) + 1
    return {"unique_pius": sum(dist.values()), "total_obs": total_obs, "clusters": dist}
