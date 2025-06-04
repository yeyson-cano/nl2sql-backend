# intent-service/app/api.py

from fastapi import APIRouter, HTTPException
from .schema import IntentRequest, IntentResponse
from .openai_client import extract_intent_with_gpt4

router = APIRouter()

# Descripción textual del esquema de la base de datos.
# En un caso real, podrías cargar esto dinámicamente.
SCHEMA_DESCRIPTION = """
clientes(id, nombre, edad),
transacciones(id, cliente_id, monto, fecha)
"""

@router.post("/api/intent", response_model=IntentResponse)
def extract_intent(req: IntentRequest):
    """
    Endpoint para analizar la intención de la consulta en lenguaje natural.
    - Envía a GPT-4 un prompt que incluye el texto del usuario y el esquema completo de la BD.
    - Devuelve directamente un JSON con 'entities', 'predicates', 'aggregations' y 'groupings'.
    """
    try:
        intent_dict = extract_intent_with_gpt4(req.text, SCHEMA_DESCRIPTION)
    except Exception as e:
        # Si GPT-4 falla o la respuesta no es JSON válido, devolvemos un error 500
        raise HTTPException(status_code=500, detail=str(e))

    # Extraemos cada lista del JSON (si alguna clave falta, devolvemos lista vacía)
    entidades     = intent_dict.get("entidades", [])
    predicados    = intent_dict.get("predicados", [])
    agregaciones  = intent_dict.get("agregaciones", [])
    agrupamientos = intent_dict.get("agrupamientos", [])

    return IntentResponse(
        entities=entidades,
        predicates=predicados,
        aggregations=agregaciones,
        groupings=agrupamientos
    )
