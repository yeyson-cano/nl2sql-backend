# intent-service/app/metrics.py

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# 1. Contador que acumula número total de peticiones
REQUEST_COUNT = Counter(
    "api_request_count",
    "Cantidad total de peticiones recibidas",
    ["method", "endpoint", "http_status"]
)

# 2. Histograma para latencia (en segundos)
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds",
    "Tiempo de latencia de las peticiones HTTP",
    ["method", "endpoint"]
)

def metrics_endpoint():
    """
    Genera la respuesta de Prometheus con todas las métricas registradas.
    """
    data = generate_latest()
    return data, CONTENT_TYPE_LATEST
