from fastapi import FastAPI
app = FastAPI(title="Intent Service")

@app.get("/health")
def health():
    return {"status": "ok"}
