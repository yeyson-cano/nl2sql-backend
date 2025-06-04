import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@patch("app.api.extract_intent_with_gpt4")
def test_api_intent_endpoint_success(mock_extract, client):
    """
    Verifica que el endpoint /api/intent:
    - Llame a extract_intent_with_gpt4 con el texto correcto.
    - Devuelva un JSON con las claves de IntentResponse.
    """
    # 1. Preparamos una respuesta simulada de extract_intent_with_gpt4
    SAMPLE = {
        "entidades": ["clientes", "transacciones.monto"],
        "predicados": [
            { "column": "transacciones.fecha", "operator": ">=", "value": "2025-01-01" }
        ],
        "agregaciones": ["SUM(transacciones.monto)"],
        "agrupamientos": ["clientes.id"]
    }
    mock_extract.return_value = SAMPLE

    # 2. Llamamos al endpoint con un JSON válido
    response = client.post("/api/intent", json={"text": "Mostrar clientes con saldo mayor a 1000"})

    # 3. Verificaciones
    assert response.status_code == 200
    data = response.json()

    #   a) Las claves del JSON de respuesta coinciden con IntentResponse
    assert "entities" in data
    assert "predicates" in data
    assert "aggregations" in data
    assert "groupings" in data

    #   b) Los valores coinciden con SAMPLE:
    assert data["entities"] == SAMPLE["entidades"]
    assert data["predicates"] == SAMPLE["predicados"]
    assert data["aggregations"] == SAMPLE["agregaciones"]
    assert data["groupings"] == SAMPLE["agrupamientos"]

    #   c) extract_intent_with_gpt4 fue llamado una sola vez con el texto y el esquema por defecto
    mock_extract.assert_called_once_with(
        "Mostrar clientes con saldo mayor a 1000",
        """
clientes(id, nombre, edad),
transacciones(id, cliente_id, monto, fecha)
"""
    )

@patch("app.api.extract_intent_with_gpt4")
def test_api_intent_endpoint_failure(mock_extract, client):
    """
    Verifica que el endpoint /api/intent maneje correctamente las excepciones
    lanzadas por extract_intent_with_gpt4 y devuelva un 500.
    """
    # 1. Hacemos que extract_intent_with_gpt4 lance una excepción
    mock_extract.side_effect = RuntimeError("Fallo en GPT-4")

    # 2. Llamamos al endpoint
    response = client.post("/api/intent", json={"text": "Texto erróneo"})

    # 3. Debe devolver 500 y en el detalle el mensaje de error
    assert response.status_code == 500
    assert "Fallo en GPT-4" in response.json()["detail"]
