# test_openai_connection.py

import os
import openai
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

# Cargar la variable de entorno desde .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("No se encontró OPENAI_API_KEY en el entorno.")

# Nuevo cliente con openai >=1.0.0
client = openai.OpenAI(api_key=api_key)

def main():
    try:
        print("Probando conexión con OpenAI GPT-4...")

        # Nueva forma de llamar a GPT-4 con la versión moderna
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": "¿Cuál es la capital de Alemania?"}
            ],
            temperature=0
        )

        # Mostrar respuesta
        content = response.choices[0].message.content.strip()
        print("✅ Conexión exitosa. Respuesta de GPT-4:")
        print(content)

    except Exception as e:
        print(f"❌ Error al conectarse con la API de OpenAI:\n{e}")

if __name__ == "__main__":
    main()
