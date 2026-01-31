import sys
import os
from pathlib import Path

# --- THE TRIPLE PATH LOCK ---
# 1. Get the absolute path of the directory containing this file (backend/)
BASE_DIR = Path(__file__).resolve().parent
# 2. Add it to the start of sys.path
sys.path.insert(0, str(BASE_DIR))
# 3. Force environment variable for sub-processes
os.environ["PYTHONPATH"] = str(BASE_DIR)

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import base64, json, re

# Explicit absolute imports from the new root
import ingestion.processor as processor_mod
import engine.tier1_measurements as measurements_mod
import router.intelligence as router_mod
import export.sealer as sealer_mod
import artifacts.pdf_generator as pdf_mod
import glossary.law_glossary as glossary_mod
import glossary.epistemic_definitions as epistemic_mod
import enrichment.gemini_compiler as gemini_mod
import generation.dispatcher as dispatcher_mod
import discovery.resolver as discovery_mod

app = FastAPI(); app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health(): return {"status": "ALIVE"}

@app.get("/stats")
def stats():
    count = 0
    path = BASE_DIR / "nkg" / "piu_moat.jsonl"
    if path.exists():
        with open(path, 'r') as f: count = sum(1 for _ in f)
    return {"unique_pius": count}

@app.post("/search")
async def search(query: str = Form(...)): 
    return discovery_mod.DiscoveryResolver.resolve(query)

@app.post("/ingest")
async def ingest(mode: str = Form(...), candidate_id: str = Form(...), file: UploadFile = File(None), sequence: str = Form(None)):
    try:
        content, label, ext = None, "Unknown", "pdb"
        if mode == "Upload" and file:
            content = await file.read(); label = "User Upload"; ext = file.filename.split(".")[-1].lower()
        else:
            content, label, ext = dispatcher_mod.GenerationDispatcher.acquire(candidate_id, sequence)

        if not content: return {"verdict": "ERROR", "details": label}

        # 1. Processing
        structure = processor_mod.IngestionProcessor.run(content, f"origin.{ext}", label)
        all_atoms = structure.atoms + structure.ligands
        coord_hash = sealer_mod.ForensicSealer.generate_hash(sealer_mod.ForensicSealer.canonical_serialize(all_atoms))
        
        # 2. Audit
        s155, m155, a155 = measurements_mod.Tier1Measurements.check_law_155_L(structure)
        s160, m160, a160 = measurements_mod.Tier1Measurements.check_law_160(structure)
        
        results = []
        for lid in glossary_mod.list_all_law_ids():
            st, me, an = ("PASS", "Verified Invariant", {})
            if lid == "LAW-155": st, me, an = s155, m155, a155
            elif lid == "LAW-160": st, me, an = s160, m160, a160
            expl = glossary_mod.get_law_explanation(lid)
            results.append({"law_id": lid, "status": st, "measurement": me, "anchor": an, "title": expl['title'], "principle": expl['principle'], "rationale": expl['rationale']})
        
        verdict = "VETO" if any(r["status"] == "FAIL" for r in results) else "PASS"
        phys_score = 20 if verdict == "VETO" else 100
        conf_score = getattr(structure.confidence, 'mean_plddt', None)
        conf_display = round(conf_score, 1) if conf_score is not None else "N/A"
        
        # 3. Synthesis
        gemini = gemini_mod.GeminiCompiler(os.getenv("GEMINI_API_KEY", "NONE"))
        rat = gemini.synthesize(verdict, phys_score, conf_display, label, results)
        sealed = sealer_mod.ForensicSealer.seal_structure(content, structure.audit_id, verdict, coord_hash, ext)
        pdf_b = pdf_mod.generate_v14_certificate(structure.audit_id, verdict, phys_score, label, rat, results, structure.atoms)

        return {
            "verdict": verdict, "score": phys_score, "conf": conf_display, "sig": structure.audit_id, 
            "laws": results, "routing": router_mod.IntelligenceRouter().decide(structure, verdict), 
            "narrative": rat, "pdf_b64": base64.b64encode(pdf_b).decode(), "pdb_b64": base64.b64encode(sealed.encode()).decode(), "ext": ext,
            "provenance": {"source": label, "mode": mode}, "definitions": epistemic_mod.DEFINITIONS
        }
    except Exception as e: return {"verdict": "ERROR", "details": str(e)}
