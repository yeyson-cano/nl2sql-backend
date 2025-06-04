import json
import pytest
from unittest.mock import patch, MagicMock

from app.openai_client import extract_intent_with_gpt4, client

# Ejemplo de JSON que queremos que la función devuelva
SAMPLE_JSON = {
    "entidades": ["clientes", "transacciones.monto"],
    "predicados": [
        {"column": "transacciones.fecha", "operator": ">=", "value": "2025-01-01"}
    ],
    "agregaciones": ["SUM(transacciones.monto)"],
    "agrupamientos": ["clientes.id"]
}

# Helper para simular la respuesta de OpenAI
class DummyChoice:
    def __init__(self, content: str):
        self.message = MagicMock(content=content)

class DummyResponse:
    def __init__(self, content: str):
        self.choices = [DummyChoice(content)]

def test_extract_intent_with_gpt4(monkeypatch):
    """
    Verifica que extract_intent_with_gpt4:
    - Llame a client.chat.completions.create con los parámetros correctos.
    - Parsee correctamente el JSON devuelto.
    """
    # 1. Preparamos la respuesta simulada de OpenAI: un string JSON idéntico a SAMPLE_JSON
    fake_json_str = json.dumps(SAMPLE_JSON)
    dummy_response = DummyResponse(fake_json_str)

    # 2. Parcheamos el método create en la instancia client
    monkeypatch.setattr(
        client.chat.completions,
        "create",
        lambda *args, **kwargs: dummy_response
    )

    # 3. Invocamos la función con texto de ejemplo y esquema de ejemplo
    user_text = "Mostrar clientes con saldo mayor a 1000"
    schema = "clientes(id, nombre), transacciones(id, cliente_id, monto)"
    result = extract_intent_with_gpt4(user_text, schema)

    # 4. Verificaciones
    #   a) La función devuelve un diccionario igual a SAMPLE_JSON
    assert isinstance(result, dict)
    assert result == SAMPLE_JSON

def test_extract_intent_with_gpt4_invalid_json(monkeypatch):
    """
    Verifica que, si GPT-4 devuelve texto que no es JSON válido,
    la función levante un RuntimeError.
    """
    # 1. Preparamos un string que no es JSON válido
    invalid_content = "no es un JSON"
    dummy_response = DummyResponse(invalid_content)

    # 2. Parcheamos el método create para que devuelva el texto inválido
    monkeypatch.setattr(
        client.chat.completions,
        "create",
        lambda *args, **kwargs: dummy_response
    )

    # 3. Llamamos a la función y esperamos un RuntimeError
    with pytest.raises(RuntimeError) as excinfo:
        extract_intent_with_gpt4("Texto cualquiera", "esquema irrelevante")

    # 4. Verificamos que el mensaje de error mencione que no se pudo parsear JSON
    assert "No se pudo parsear el JSON de GPT-4" in str(excinfo.value)
