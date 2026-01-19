from .worker_app import celery_app
from .physics_engine import SovereignEngine
from .adversarial_engine import AdversarialEngine
from app.core.database import SessionLocal
from app.models.job import Job
from app.models.nkg import NKGRegistry
from datetime import datetime

@celery_app.task(name="run_sovereign_sieve_pipeline")
def run_sovereign_sieve_pipeline(job_id: str, file_path: str, target: str, binder: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job: return
        job.status = "running"
        
        # TIER 1
        job.current_stage = "TIER_1: GEOMETRIC_AUDIT"
        db.commit()
        metrics = SovereignEngine.run_audit(file_path, target, binder)
        
        # TIER 3
        job.current_stage = "TIER_3: ADVERSARIAL_CHECK"
        db.commit()
        adv = AdversarialEngine.compare_to_reference(file_path, target, binder)
        metrics["adversarial"] = adv
        
        # VERDICT
        job.current_stage = "FINALIZING_VERDICT"
        db.commit()
        v_status, p_law = SovereignEngine.calculate_verdict(metrics)

        if v_status == "PHYSICS_VETO" and p_law:
            nkg_entry = NKGRegistry(
                job_id=job_id,
                primary_law=p_law,
                secondary_laws=metrics.get('laws_violated', [])[1:]
            )
            db.add(nkg_entry)

        job.status = "completed"
        job.current_stage = "VERDICT_READY"
        job.verdict = v_status
        job.metrics = metrics
        job.completed_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "failed"
            job.current_stage = f"ERROR: {str(e)}"
            db.commit()
    finally:
        db.close()
