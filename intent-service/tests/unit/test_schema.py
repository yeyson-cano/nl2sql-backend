import pytest
from pydantic import ValidationError

from app.schema import IntentRequest, IntentResponse, Predicate

def test_intent_request_valid():
    # Debe aceptar un request con texto
    req = IntentRequest(text="Mostrar clientes con saldo > 1000")
    assert req.text == "Mostrar clientes con saldo > 1000"

def test_intent_request_missing_text():
    # Debe fallar si falta el campo 'text'
    with pytest.raises(ValidationError) as excinfo:
        IntentRequest()  # sin argumentos
    # Mensaje de error debería mencionar 'text'
    assert "text" in str(excinfo.value)

def test_intent_request_wrong_type():
    # Debe fallar si 'text' no es string
    with pytest.raises(ValidationError):
        IntentRequest(text=12345)

def test_intent_response_defaults():
    # Sin pasar nada, las listas deben inicializarse vacías
    resp = IntentResponse(entities=["tabla"], predicates=[], aggregations=[], groupings=[])
    assert resp.entities == ["tabla"]
    assert resp.predicates == []
    assert resp.aggregations == []
    assert resp.groupings == []

def test_predicate_model():
    # Construcción y acceso a campos del Predicate
    p = Predicate(column="clientes.id", operator=">", value="100")
    assert p.column == "clientes.id"
    assert p.operator == ">"
    assert p.value == "100"
