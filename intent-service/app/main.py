# intent-service/app/main.py

from fastapi import FastAPI
from .api import router as intent_router  # importamos el router definido en api.py

app = FastAPI(title="Intent Service")

# Montamos el router sin prefijo adicional, de modo que /api/intent quede expuesto
app.include_router(intent_router)

@app.get("/health")
def health():
    return {"status": "ok"}
