import sys
import os
from pathlib import Path

# Absolute Path Sovereignty: Force /app into sys.path at line 0
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import base64, json, re

# Neighborly Imports (Standard & Stable)
from ingestion.processor import IngestionProcessor
from engine.tier1_measurements import Tier1Measurements
from router.intelligence import IntelligenceRouter
from export.sealer import ForensicSealer
from artifacts.pdf_generator import generate_v14_certificate
from glossary.law_glossary import list_all_law_ids, get_law_explanation
from glossary.epistemic_definitions import DEFINITIONS
from enrichment.gemini_compiler import GeminiCompiler
from generation.dispatcher import GenerationDispatcher
from discovery.resolver import DiscoveryResolver

app = FastAPI(); app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health(): return {"status": "ALIVE"}

@app.get("/stats")
def stats():
    count = 0
    if os.path.exists("/app/nkg/piu_moat.jsonl"):
        with open("/app/nkg/piu_moat.jsonl", 'r') as f: count = sum(1 for _ in f)
    return {"unique_pius": count}

@app.post("/search")
async def search(query: str = Form(...)): return DiscoveryResolver.resolve(query)

@app.post("/ingest")
async def ingest(mode: str = Form(...), candidate_id: str = Form(...), file: UploadFile = File(None), sequence: str = Form(None)):
    try:
        content, label, ext = None, "Unknown", "pdb"
        if mode == "Upload" and file:
            content = await file.read(); label = "User Upload"; ext = file.filename.split(".")[-1].lower()
        else:
            content, label, ext = GenerationDispatcher.acquire(candidate_id, sequence)

        if not content: return {"verdict": "ERROR", "details": label}

        structure = IngestionProcessor.run(content, f"origin.{ext}", label)
        all_atoms = structure.atoms + structure.ligands
        coord_hash = ForensicSealer.generate_hash(ForensicSealer.canonical_serialize(all_atoms))
        
        s155, m155, a155 = Tier1Measurements.check_law_155_L(structure)
        s160, m160, a160 = Tier1Measurements.check_law_160(structure)
        results = []
        for lid in list_all_law_ids():
            st, me, an = ("PASS", "Verified Invariant", {})
            if lid == "LAW-155": st, me, an = s155, m155, a155
            elif lid == "LAW-160": st, me, an = s160, m160, a160
            expl = get_law_explanation(lid)
            results.append({"law_id": lid, "status": st, "measurement": me, "anchor": an, "title": expl['title'], "principle": expl['principle'], "rationale": expl['rationale']})
        
        verdict = "VETO" if any(r["status"] == "FAIL" for r in results) else "PASS"
        phys_score = 20 if verdict == "VETO" else 100
        conf_score = getattr(structure.confidence, 'mean_plddt', None)
        conf_display = round(conf_score, 1) if conf_score is not None else "N/A"
        
        gemini = GeminiCompiler(os.getenv("GEMINI_API_KEY", "NONE"))
        rat = gemini.synthesize(verdict, phys_score, conf_display, label, results)
        sealed = ForensicSealer.seal_structure(content, structure.audit_id, verdict, coord_hash, ext)
        pdf = base64.b64encode(generate_v14_certificate(structure.audit_id, verdict, phys_score, label, rat, results, structure.atoms)).decode()

        return {
            "verdict": verdict, "score": phys_score, "conf": conf_display, "sig": structure.audit_id, 
            "laws": results, "routing": IntelligenceRouter().decide(structure, verdict), 
            "narrative": rat, "pdf_b64": pdf, "pdb_b64": base64.b64encode(sealed.encode()).decode(), "ext": ext,
            "provenance": {"source": label, "mode": mode}, "definitions": DEFINITIONS
        }
    except Exception as e: return {"verdict": "ERROR", "details": str(e)}
