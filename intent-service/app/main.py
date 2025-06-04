# intent-service/app/main.py

import logging
import time
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import CONTENT_TYPE_LATEST
from .metrics import REQUEST_COUNT, REQUEST_LATENCY, metrics_endpoint
from .api import router as intent_router

# ---------------------------------------------------
# 1. CONFIGURACIÓN BÁSICA DE LOGGING
# ---------------------------------------------------
# Creamos un logger de aplicación con formato sencillo
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("intent_service")

# ---------------------------------------------------
# 2. CREAR LA APP FASTAPI E INCLUIR EL ROUTER PRINCIPAL
# ---------------------------------------------------
app = FastAPI(
    title="Intent Service",
    description="Servicio para extraer intenciones y métricas",
    version="1.0.0"
)

app.include_router(intent_router)  # monta /api/intent, etc.


# ---------------------------------------------------
# 3. MIDDLEWARE PARA LOGS Y MÉTRICAS
# ---------------------------------------------------
class LoggingAndMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Este middleware:
         - Mide el tiempo de ejecución (latencia).
         - Ejecuta la petición.
         - Registra un log con método, ruta, status y latencia.
         - Incrementa contadores y histogramas de Prometheus.
        """
        start_time = time.time()
        response: Response = await call_next(request)
        process_time = time.time() - start_time

        # Extraer datos relevantes
        method = request.method
        path = request.url.path
        status_code = response.status_code

        # 1. LOG
        logger.info(f"{method} {path} → {status_code} [{process_time:.3f}s]")

        # 2. METRICS
        REQUEST_COUNT.labels(method=method, endpoint=path, http_status=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path).observe(process_time)

        return response

# Instalar el middleware en la aplicación
app.add_middleware(LoggingAndMetricsMiddleware)


# ---------------------------------------------------
# 4. ENDPOINT /metrics
# ---------------------------------------------------
@app.get("/metrics")
async def metrics():
    """
    Exponer métricas en formato Prometheus.
    """
    data, content_type = metrics_endpoint()
    return Response(content=data, media_type=content_type)


# ---------------------------------------------------
# 5. ENDPOINT DE HEALTHCHECK (opcional)
# ---------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}
