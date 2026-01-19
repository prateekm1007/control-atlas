from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job
from app.worker import run_job
import uuid
import os

router = APIRouter(prefix="/jobs", tags=["jobs"])

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
def upload_job(
    file: UploadFile = File(...),
    target_chain: str = Form(...),
    binder_chain: str = Form(...),
    db: Session = Depends(get_db)
):
    # --- Persist file ---
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # --- CREATE JOB ROW (EXPLICIT) ---
    job = Job(
        id=job_id,
        status="queued",
        current_stage="UPLOADED",
        verdict=None,
        file_path=file_path,
        target_chain=target_chain,
        binder_chain=binder_chain
    )

    db.add(job)
    db.commit()          # 🔴 THIS WAS MISSING OR NOT GUARANTEED
    db.refresh(job)      # 🔴 ENSURES ID EXISTS

    print(f"[JOB CREATED] id={job.id} status={job.status}")

    # --- DISPATCH TO WORKER ---
    run_job.delay(job.id)

    return {"job_id": job.id}
