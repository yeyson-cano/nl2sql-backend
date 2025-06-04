# intent-service/app/openai_client.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# Carga variables de entorno desde .env
load_dotenv(find_dotenv(), override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Falta la variable OPENAI_API_KEY en el entorno")

# Cliente de OpenAI para API >=1.0.0
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_intent_with_gpt4(user_text: str, schema_description: str) -> dict:
    """
    Llama a GPT-4 para extraer entidades, predicados, agregaciones y agrupamientos.

    Args:
        user_text: Consulta del usuario en lenguaje natural.
        schema_description: Esquema textual de las tablas y columnas disponibles.

    Retorna:
        Diccionario con claves:
          - "entidades": lista de objetos { "name": ..., "type": "TABLE" | "COLUMN" | ... }
          - "predicados": lista de { "column": ..., "operator": ..., "value": ... }
          - "agregaciones": lista de funciones tipo "SUM(...)" o "AVG(...)"
          - "agrupamientos": lista de columnas para GROUP BY
    """
    prompt = f"""
Dada la siguiente consulta en lenguaje natural y el esquema de la base de datos, devuelve únicamente un JSON con estas claves:
- "entidades": lista de objetos con "name" (nombre de entidad) y "type" (puede ser TABLE, COLUMN, VALUE, etc.).
- "predicados": lista de objetos {{ "column": ..., "operator": ..., "value": ... }}.
- "agregaciones": lista de funciones de agregación como "SUM(transacciones.monto)".
- "agrupamientos": lista de columnas usadas en GROUP BY.

Esquema:
{schema_description}

Consulta: "{user_text}"

Respuesta en JSON:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente que traduce intenciones a JSON estructurado."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=500,
        )
    except Exception as e:
        raise RuntimeError(f"Error en la llamada a GPT-4: {e}")

    content = response.choices[0].message.content.strip()

    try:
        intent_json = json.loads(content)
    except Exception as e:
        raise RuntimeError(f"No se pudo parsear el JSON de GPT-4: {e}\nRespuesta recibida:\n{content}")

    return intent_json
