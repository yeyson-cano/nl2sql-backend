# intent-service/app/utils.py

import re
from typing import List, Dict

def extract_predicates(text: str) -> List[Dict[str, str]]:
    """
    Identifica predicados (comparadores y valores) en la cadena `text`.
    Soporta:
      - Operadores: >, <, >=, <=, =
      - BETWEEN ... AND ...
    Retorna una lista de diccionarios con claves:
      - "column": nombre de la columna (cadena previa al operador)
      - "operator": comparador encontrado ("<", ">", "<=", ">=", "=", "BETWEEN")
      - "value": valor asociado; en caso de BETWEEN, la forma "valor1 AND valor2".
    """
    predicates = []

    # 1) Detectar expresiones BETWEEN ... AND ...
    pattern_between = re.compile(
        r"(?P<column>\b\w[\w\.]*\b)\s+BETWEEN\s+(?P<val1>[^ ]+)\s+AND\s+(?P<val2>[^ ]+)",
        flags=re.IGNORECASE
    )
    for m in pattern_between.finditer(text):
        col = m.group("column")
        val1 = m.group("val1")
        val2 = m.group("val2")
        predicates.append({
            "column": col,
            "operator": "BETWEEN",
            "value": f"{val1} AND {val2}"
        })

    # 2) Detectar comparadores simples: >=, <=, >, <, =
    pattern_simple = re.compile(
        r"(?P<column>\b\w[\w\.]*\b)\s*(?P<op>>=|<=|=|>|<)\s*(?P<value>[^ ,]+)",
        flags=re.IGNORECASE
    )
    for m in pattern_simple.finditer(text):
        col = m.group("column")
        op = m.group("op")
        val = m.group("value")
        # Evitar duplicar si ya capturamos un BETWEEN para la misma columna
        exists_between = any(
            p["column"].lower() == col.lower() and p["operator"].upper() == "BETWEEN"
            for p in predicates
        )
        if not exists_between:
            predicates.append({
                "column": col,
                "operator": op,
                "value": val
            })

    return predicates


def extract_aggregations(text: str) -> List[str]:
    """
    Extrae funciones de agregación del texto. Reconoce tanto keywords en inglés
    (SUM, COUNT, AVG, MIN, MAX) como sus equivalentes en español (Suma, Conteo, Promedio).

    Retorna una lista de strings con la forma "FUNCION(columna)".
    """
    aggs: List[str] = []

    # 1) Patrones en inglés: SUM(...), COUNT(...), AVG(...), MIN(...), MAX(...)
    pattern_english = re.compile(
        r"(?P<func>SUM|COUNT|AVG|MIN|MAX)\s*\(\s*(?P<column>[\w\.]+)\s*\)",
        flags=re.IGNORECASE
    )
    for m in pattern_english.finditer(text):
        func = m.group("func").upper()
        col = m.group("column")
        aggs.append(f"{func}({col})")

    # 2) Patrones en español: "Suma de columna", "Conteo de columna", "Promedio de columna"
    pattern_spanish = re.compile(
        r"(?P<func>Suma|Conteo|Promedio)\s+de\s+(?P<column>[\w\.]+)",
        flags=re.IGNORECASE
    )
    for m in pattern_spanish.finditer(text):
        func_span = m.group("func").lower()
        col = m.group("column")
        mapping = {
            "suma": "SUM",
            "conteo": "COUNT",
            "promedio": "AVG"
        }
        func = mapping.get(func_span, func_span).upper()
        aggs.append(f"{func}({col})")

    return aggs


def extract_groupings(text: str) -> List[str]:
    """
    Extrae columnas utilizadas en agrupamiento. Reconoce:
      1. "GROUP BY columna1, columna2[, ...]"
      2. "por columna" o "por columna1 y columna2" en español.

    Retorna una lista de nombres de columna sin duplicar.
    """
    groupings: List[str] = []

    # 1) Patrón SQL en inglés: GROUP BY col1, col2, ...
    pattern_group_by = re.compile(
        r"GROUP\s+BY\s+(?P<cols>[\w\.,\s]+)",
        flags=re.IGNORECASE
    )
    match_gb = pattern_group_by.search(text)
    if match_gb:
        cols = match_gb.group("cols")
        # Dividir por comas y procesar cada fragmento:
        for part in cols.split(","):
            part = part.strip()
            if not part:
                continue
            # Si el fragmento comienza con la palabra "por" -> lo ignoramos
            if re.match(r"^por\b", part, flags=re.IGNORECASE):
                continue
            # Dividir mediante " y "
            for col in re.split(r"\s+y\s+", part, flags=re.IGNORECASE):
                col_clean = col.strip()
                if col_clean:
                    groupings.append(col_clean)
        return groupings

    # 2) Patrón en español: "por columna1 y columna2" o "por columna"
    pattern_spanish_por = re.compile(
        r"\bpor\s+(?P<cols>[\w\.]+(?:\s+y\s+[\w\.]+)*)",
        flags=re.IGNORECASE
    )
    match_por = pattern_spanish_por.search(text)
    if match_por:
        cols = match_por.group("cols")
        for col in re.split(r"\s+y\s+", cols, flags=re.IGNORECASE):
            col_clean = col.strip()
            if col_clean:
                groupings.append(col_clean)
        return groupings

    return groupings
