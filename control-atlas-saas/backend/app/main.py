from fastapi import FastAPI
from app.routes import jobs, nkg, auth

app = FastAPI(title="Sovereign Sieve API")

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(nkg.router)
