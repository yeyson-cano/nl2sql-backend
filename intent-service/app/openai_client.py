# intent-service/app/openai_client.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# Carga variables de entorno desde .env (usa find_dotenv para encontrarlo en carpetas superiores)
load_dotenv(find_dotenv(), override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Falta la variable OPENAI_API_KEY en el entorno")

# Instancia del cliente de OpenAI (versión >=1.0.0)
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_intent_with_gpt4(user_text: str, schema_description: str) -> dict:
    """
    Llama a GPT-4 para extraer entidades, predicados, agregaciones y agrupamientos.

    Args:
        user_text: La consulta en lenguaje natural del usuario.
        schema_description: Descripción textual del esquema de la base de datos
                            (tablas, columnas y tipos) a incluir en el prompt.

    Retorna:
        Un diccionario con las claves:
          - "entidades": lista de tablas/columnas mencionadas.
          - "predicados": lista de objetos {"column": ..., "operator": ..., "value": ...}.
          - "agregaciones": lista de funciones de agregación (e.g., "SUM(transacciones.monto)").
          - "agrupamientos": lista de columnas para GROUP BY.

    Lanza:
        RuntimeError si la llamada a la API falla o la respuesta no es un JSON válido.
    """
    prompt = f"""
Dada la siguiente consulta en lenguaje natural y el esquema de la base de datos, devuelve únicamente un JSON con estas claves:
  - "entidades": lista de tablas y columnas mencionadas.
  - "predicados": lista de objetos {{ "column": ..., "operator": ..., "value": ... }}.
  - "agregaciones": lista de funciones de agregación (por ejemplo, "SUM(transacciones.monto)").
  - "agrupamientos": lista de columnas para GROUP BY.

Esquema:
{schema_description}

Consulta: "{user_text}"

Respuesta en JSON:
"""

    try:
        # Nueva forma de llamar a GPT-4 con openai>=1.0.0
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente que traduce intenciones a JSON estructurado."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,  # determinista para mayor consistencia
            max_tokens=500,
        )
    except Exception as e:
        raise RuntimeError(f"Error en la llamada a GPT-4: {e}")

    # Extraer el contenido generado por GPT-4
    content = response.choices[0].message.content.strip()

    try:
        intent_json = json.loads(content)
    except Exception as e:
        raise RuntimeError(f"No se pudo parsear el JSON de GPT-4: {e}\nRespuesta recibida:\n{content}")

    return intent_json
