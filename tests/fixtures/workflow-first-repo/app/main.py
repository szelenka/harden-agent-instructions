from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/workflow")
def workflow() -> dict:
    return {"name": "workflow"}
