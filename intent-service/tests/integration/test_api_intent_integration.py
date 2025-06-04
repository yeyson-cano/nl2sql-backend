import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

@patch("app.api.extract_intent_with_gpt4")
def test_integration_api_intent_with_mocked_gpt4(mock_extract):
    """
    Prueba de integración completa para /api/intent:
    - Simula la respuesta de GPT-4 con tipos de entidades.
    - Llama al endpoint real de FastAPI.
    - Verifica que solo se incluyan entidades tipo TABLE y COLUMN.
    """

    # 1. Simulamos una respuesta que incluye entidades de distintos tipos
    simulated_response = {
        "entidades": [
            {"name": "clientes", "type": "TABLE"},
            {"name": "transacciones.monto", "type": "COLUMN"},
            {"name": ">= 1000", "type": "VALUE"},
            {"name": "agrupado_por", "type": "KEYWORD"}  # No debe ser incluido
        ],
        "predicados": [
            {"column": "transacciones.fecha", "operator": ">=", "value": "2025-01-01"}
        ],
        "agregaciones": ["SUM(transacciones.monto)"],
        "agrupamientos": ["clientes.id"]
    }
    mock_extract.return_value = simulated_response

    # 2. Enviamos una petición real al endpoint
    response = client.post("/api/intent", json={"text": "Mostrar clientes con saldo mayor a 1000"})

    # 3. Verificamos que la API devuelva solo los nombres de entidades tipo TABLE y COLUMN
    assert response.status_code == 200
    data = response.json()

    assert data["entities"] == ["clientes", "transacciones.monto"]  # Solo los válidos
    assert data["predicates"] == simulated_response["predicados"]
    assert data["aggregations"] == simulated_response["agregaciones"]
    assert data["groupings"] == simulated_response["agrupamientos"]
