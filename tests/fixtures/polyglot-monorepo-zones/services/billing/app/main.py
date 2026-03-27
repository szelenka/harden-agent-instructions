"""Billing service entry point."""

from fastapi import FastAPI

app = FastAPI(title="Billing Service")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/invoices")
def create_invoice():
    return {"id": "inv_001", "status": "created"}
