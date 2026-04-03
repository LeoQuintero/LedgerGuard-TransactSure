from fastapi import FastAPI
from app.database import engine, Base
from app import models  # noqa: F401  ←  importa los modelos para que Base los registre

app = FastAPI(
    title="LedgerGuard-TransactSure",
    description="Data Quality Automation for Fintech/Banking",
    version="0.1.0"
)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "LedgerGuard-TransactSure"}