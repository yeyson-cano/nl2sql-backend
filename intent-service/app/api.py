# intent-service/app/api.py

from fastapi import APIRouter, HTTPException
from .schema import IntentRequest, IntentResponse
from .openai_client import extract_intent_with_gpt4

router = APIRouter()

# Esquema simulado. En una app real esto se puede extraer dinámicamente desde la BD.
SCHEMA_DESCRIPTION = """
clientes(id, nombre, edad),
transacciones(id, cliente_id, monto, fecha)
"""

@router.post("/api/intent", response_model=IntentResponse)
def extract_intent(req: IntentRequest):
    """
    Endpoint para analizar la intención de la consulta en lenguaje natural.
    - Llama a GPT-4 con el texto del usuario y un esquema de ejemplo.
    - Filtra y transforma la salida para ajustarse al modelo de respuesta.
    """
    try:
        intent_dict = extract_intent_with_gpt4(req.text, SCHEMA_DESCRIPTION)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Extraemos y filtramos solo entidades de tipo TABLE o COLUMN
    raw_entidades = intent_dict.get("entidades", [])
    entidades = [
        e["name"] for e in raw_entidades
        if isinstance(e, dict) and e.get("type") in ("TABLE", "COLUMN")
    ]

    # Se asume que los demás campos ya vienen con la forma esperada
    predicados = intent_dict.get("predicados", [])
    agregaciones = intent_dict.get("agregaciones", [])
    agrupamientos = intent_dict.get("agrupamientos", [])

    return IntentResponse(
        entities=entidades,
        predicates=predicados,
        aggregations=agregaciones,
        groupings=agrupamientos
    )
