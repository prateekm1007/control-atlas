from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import hashlib, base64, json, sys, os
sys.path.append("/app")

from ingestion.processor import IngestionProcessor
from engine.tier1_measurements import Tier1Measurements
from router.intelligence import IntelligenceRouter
from export.sealer import ForensicSealer
from artifacts.pdf_generator import generate_v14_certificate
from glossary.law_glossary import get_law_explanation, list_all_law_ids
from enrichment.gemini_compiler import GeminiCompiler

app = FastAPI(); app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health(): return {"status": "ALIVE"}

@app.get("/stats")
def stats():
    count = 0
    if os.path.exists("/app/nkg/piu_moat.jsonl"):
        with open("/app/nkg/piu_moat.jsonl", 'r') as f: count = sum(1 for _ in f)
    return {"unique_pius": count}

@app.post("/audit")
async def audit(file: UploadFile = File(...), generator: str = Form("Unknown")):
    try:
        content = await file.read(); ext = file.filename.split(".")[-1].lower()
        if ext not in ["pdb", "cif"]: ext = "pdb"
        
        structure = IngestionProcessor.run(content, file.filename, generator)
        s155, m155, a155 = Tier1Measurements.check_law_155_L(structure)
        s160, m160, a160 = Tier1Measurements.check_law_160(structure)
        
        results = []
        for lid in list_all_law_ids():
            status, meas, anch = "PASS", "Verified", {}
            if lid == "LAW-155": status, meas, anch = s155, m155, a155
            elif lid == "LAW-160": status, meas, anch = s160, m160, a160
            results.append({"law_id": lid, "status": status, "measurement": meas, "anchor": anch, **get_law_explanation(lid)})

        final_verdict = "VETO" if any(r["status"] == "FAIL" for r in results) else "PASS"
        score = 20 if final_verdict == "VETO" else 100
        
        gemini = GeminiCompiler(os.getenv("GEMINI_API_KEY", "NONE"))
        rat = gemini.synthesize(final_verdict, score, generator, results)
        
        sealed_pdb = ForensicSealer.seal_pdb(content.decode(errors='ignore'), structure.audit_id, final_verdict, structure.get_coordinate_hash())
        
        pdf_b64 = None
        try: pdf_b64 = base64.b64encode(generate_v14_certificate(structure.audit_id, final_verdict, score, generator, rat, results, structure.atoms)).decode()
        except: pass

        return {
            "verdict": final_verdict, "score": score, "sig": structure.audit_id, 
            "laws": results, "routing": IntelligenceRouter().decide(structure, final_verdict), "narrative": rat, 
            "pdf_b64": pdf_b64, "pdb_b64": base64.b64encode(sealed_pdb.encode()).decode(), "ext": ext
        }
    except Exception as e: return {"verdict": "ERROR", "details": str(e)}
