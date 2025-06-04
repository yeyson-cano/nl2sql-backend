# intent-service/tests/integration/test_api_intent_full_response.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)

@patch("app.api.extract_intent_with_gpt4")
def test_api_intent_full_json_response(mock_extract):
    """
    Test de integración que:
     - Simula la salida de GPT-4 (los 4 bloques: entidades, predicados, agregaciones, agrupamientos).
     - Llama al endpoint /api/intent.
     - Compara la respuesta JSON completa con un JSON "gold" predefinido.
    """

    # 1. Definimos el "gold" que queremos recibir.
    GOLD_RESPONSE = {
        # Raw de GPT-4 incluiría objetos tipo { "name": ..., "type": ... }
        # Pero el endpoint filtra y devuelve sólo "name" en entities.
        "entities": [
            "clientes",
            "transacciones.monto"
        ],
        "predicates": [
            {
                "column": "transacciones.fecha",
                "operator": ">=",
                "value": "2025-01-01"
            }
        ],
        "aggregations": [
            "SUM(transacciones.monto)"
        ],
        "groupings": [
            "clientes.id"
        ]
    }

    # 2. Configuramos el mock de extract_intent_with_gpt4 para devolver un dict “raw”
    #    donde "entidades" trae una lista de objetos con name/type.
    raw_mock = {
        "entidades": [
            {"name": "clientes", "type": "TABLE"},
            {"name": "transacciones.monto", "type": "COLUMN"},
            {"name": "1000", "type": "VALUE"}  # no debe aparecer en la respuesta final
        ],
        "predicados": [
            {
                "column": "transacciones.fecha",
                "operator": ">=",
                "value": "2025-01-01"
            }
        ],
        "agregaciones": [
            "SUM(transacciones.monto)"
        ],
        "agrupamientos": [
            "clientes.id"
        ]
    }
    mock_extract.return_value = raw_mock

    # 3. Hacemos la petición real al endpoint
    response = client.post(
        "/api/intent",
        json={"text": "Mostrar clientes con saldo mayor a 1000"}
    )
    assert response.status_code == 200

    # 4. Obtenemos la respuesta JSON y la comparamos en su totalidad con el GOLD_RESPONSE
    data = response.json()

    # Verificación completa de igualdad de los 4 campos (order no importará porque son listas)
    assert set(data["entities"]) == set(GOLD_RESPONSE["entities"])
    assert data["predicates"] == GOLD_RESPONSE["predicates"]
    assert data["aggregations"] == GOLD_RESPONSE["aggregations"]
    assert data["groupings"] == GOLD_RESPONSE["groupings"]

    # Alternativamente, para comparar el dict completo sin raw order:
    # assert data == GOLD_RESPONSE
