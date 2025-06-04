# tests/unit/test_openai_client.py

import json
import pytest
from unittest.mock import MagicMock
from app.openai_client import extract_intent_with_gpt4, client

# JSON simulado con entidades tipadas
SAMPLE_JSON = {
    "entidades": [
        {"name": "clientes", "type": "TABLE"},
        {"name": "transacciones.monto", "type": "COLUMN"},
        {"name": "2025-01-01", "type": "VALUE"}
    ],
    "predicados": [
        {"column": "transacciones.fecha", "operator": ">=", "value": "2025-01-01"}
    ],
    "agregaciones": ["SUM(transacciones.monto)"],
    "agrupamientos": ["clientes.id"]
}

# Helpers para simular respuestas de OpenAI
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
    fake_json_str = json.dumps(SAMPLE_JSON)
    dummy_response = DummyResponse(fake_json_str)

    # Parcheamos client.chat.completions.create para devolver el dummy
    monkeypatch.setattr(
        client.chat.completions,
        "create",
        lambda *args, **kwargs: dummy_response
    )

    user_text = "Mostrar clientes con saldo mayor a 1000"
    schema = "clientes(id, nombre), transacciones(id, cliente_id, monto)"
    result = extract_intent_with_gpt4(user_text, schema)

    assert isinstance(result, dict)
    assert result == SAMPLE_JSON
    assert all("name" in e and "type" in e for e in result["entidades"])

def test_extract_intent_with_gpt4_invalid_json(monkeypatch):
    """
    Verifica que, si GPT-4 devuelve texto que no es JSON válido,
    se lanza un RuntimeError.
    """
    dummy_response = DummyResponse("no es un JSON")

    monkeypatch.setattr(
        client.chat.completions,
        "create",
        lambda *args, **kwargs: dummy_response
    )

    with pytest.raises(RuntimeError) as excinfo:
        extract_intent_with_gpt4("Texto cualquiera", "esquema irrelevante")

    assert "No se pudo parsear el JSON de GPT-4" in str(excinfo.value)
