import os
import requests
from .utils import extract_sql

# Local GPT4All API base (can override via .env)
API_BASE = os.getenv('OPENAI_API_BASE', 'http://localhost:4891/v1')
CHAT_URL = f"{API_BASE}/chat/completions"


def generate_sql_sketch(prompt: str,
                        model: str = 'Llama-3-8B-Instruct',
                        temperature: float = 0.2,
                        max_tokens: int = 512) -> str:
    """
    Call local GPT4All API to generate a SQL skeleton and extract the pure SQL.
    """
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': temperature,
        'max_tokens': max_tokens
    }
    resp = requests.post(CHAT_URL, json=payload)
    resp.raise_for_status()
    data = resp.json()
    raw = data['choices'][0]['message']['content']
    # Extract only the SQL SELECT statement
    sql = extract_sql(raw)
    return sql