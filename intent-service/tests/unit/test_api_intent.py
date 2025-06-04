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
    - Devuelva un JSON con claves correctas y entidades filtradas correctamente.
    """
    # 1. Respuesta simulada con tipos mixtos
    SAMPLE = {
        "entidades": [
            {"name": "clientes", "type": "TABLE"},
            {"name": "transacciones.monto", "type": "COLUMN"},
            {"name": ">= 1000", "type": "VALUE"}  # debe ser filtrado
        ],
        "predicados": [
            {"column": "transacciones.fecha", "operator": ">=", "value": "2025-01-01"}
        ],
        "agregaciones": ["SUM(transacciones.monto)"],
        "agrupamientos": ["clientes.id"]
    }
    mock_extract.return_value = SAMPLE

    # 2. Enviamos la solicitud al endpoint
    response = client.post("/api/intent", json={"text": "Mostrar clientes con saldo mayor a 1000"})

    # 3. Verificamos respuesta
    assert response.status_code == 200
    data = response.json()

    # a) Claves esperadas en la respuesta
    assert "entities" in data
    assert "predicates" in data
    assert "aggregations" in data
    assert "groupings" in data

    # b) Se espera que solo TABLE y COLUMN estén presentes
    assert data["entities"] == ["clientes", "transacciones.monto"]
    assert data["predicates"] == SAMPLE["predicados"]
    assert data["aggregations"] == SAMPLE["agregaciones"]
    assert data["groupings"] == SAMPLE["agrupamientos"]

    # c) Validamos que se llamó con los parámetros esperados
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
    Verifica que el endpoint /api/intent maneje correctamente excepciones
    y devuelva un error 500 con detalle.
    """
    mock_extract.side_effect = RuntimeError("Fallo en GPT-4")

    response = client.post("/api/intent", json={"text": "Texto erróneo"})

    assert response.status_code == 500
    assert "Fallo en GPT-4" in response.json()["detail"]
