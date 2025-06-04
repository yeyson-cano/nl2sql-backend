# intent-service/tests/unit/test_utils.py

import pytest
from app.utils import extract_predicates, extract_aggregations, extract_groupings

# --------------------------------------
# Tests para extract_predicates
# --------------------------------------
@pytest.mark.parametrize("text, expected", [
    # 1. Comparador >
    ("edad > 18", [
        {"column": "edad", "operator": ">", "value": "18"}
    ]),
    # 2. Comparador >=
    ("saldo >= 1000", [
        {"column": "saldo", "operator": ">=", "value": "1000"}
    ]),
    # 3. Comparador <=
    ("precio <= 50.5", [
        {"column": "precio", "operator": "<=", "value": "50.5"}
    ]),
    # 4. Comparador =
    ("fecha = 2025-01-01", [
        {"column": "fecha", "operator": "=", "value": "2025-01-01"}
    ]),
    # 5. BETWEEN ... AND ...
    ("puntaje BETWEEN 10 AND 20", [
        {"column": "puntaje", "operator": "BETWEEN", "value": "10 AND 20"}
    ]),
    # 6. Mezcla de BETWEEN y comparadores simples; BETWEEN debe prevalecer
    ("puntaje BETWEEN 10 AND 20 y puntaje > 5", [
        {"column": "puntaje", "operator": "BETWEEN", "value": "10 AND 20"}
    ]),
    # 7. Varios predicados separados por comas
    ("edad > 18, saldo < 500, fecha = 2025-12-31", [
        {"column": "edad", "operator": ">", "value": "18"},
        {"column": "saldo", "operator": "<", "value": "500"},
        {"column": "fecha", "operator": "=", "value": "2025-12-31"}
    ]),
    # 8. Texto sin predicados
    ("Mostrar todos los clientes", [])
])
def test_extract_predicates_various(text, expected):
    """
    Comprueba que extract_predicates detecte correctamente
    diferentes tipos de predicados en una cadena de texto.
    """
    result = extract_predicates(text)
    result_set = {(p["column"], p["operator"], p["value"]) for p in result}
    expected_set = {(p["column"], p["operator"], p["value"]) for p in expected}
    assert result_set == expected_set


# --------------------------------------
# Tests para extract_aggregations
# --------------------------------------
@pytest.mark.parametrize("text, expected", [
    # 1. Inglés con paréntesis
    ("Obtener SUM(saldo) y COUNT(clientes)", ["SUM(saldo)", "COUNT(clientes)"]),
    # 2. Inglés con minúsculas
    ("La función avg(ventas) debe usarse", ["AVG(ventas)"]),
    # 3. Español: "Promedio de ventas"
    ("Necesito el Promedio de ventas por cliente", ["AVG(ventas)"]),
    # 4. Español: "Suma de monto"
    ("Calcular la Suma de monto total", ["SUM(monto)"]),
    # 5. Español: "Conteo de transacciones"
    ("Mostrar Conteo de transacciones por día", ["COUNT(transacciones)"]),
    # 6. No hay función de agregación
    ("Solo lista de clientes ordenados", [])
])
def test_extract_aggregations_various(text, expected):
    """
    Comprueba que extract_aggregations detecte correctamente
    funciones de agregación en una cadena de texto.
    """
    result = extract_aggregations(text)
    assert set(result) == set(expected)


# --------------------------------------
# Tests para extract_groupings
# --------------------------------------
@pytest.mark.parametrize("text, expected", [
    # 1. Inglés: GROUP BY
    ("SELECT SUM(saldo) FROM transacciones GROUP BY cliente, región",
     ["cliente", "región"]),
    # 2. Español simple: "por cliente"
    ("Promedio de ventas por cliente", ["cliente"]),
    # 3. Español con varios: "por producto y mes"
    ("Total vendido por producto y mes", ["producto", "mes"]),
    # 4. Español con mayúsculas/minúsculas variadas
    ("Cantidad total POR región", ["región"]),
    # 5. Mezcla de patrones (prefiere GROUP BY)
    ("Suma de monto GROUP BY mes y región, por cliente",
     ["mes", "región"]),
    # 6. No hay agrupamiento explícito
    ("Listado completo de clientes", [])
])
def test_extract_groupings_various(text, expected):
    """
    Comprueba que extract_groupings detecte correctamente
    columnas para agrupamiento en una cadena de texto.
    """
    result = extract_groupings(text)
    assert set(result) == set(expected)
