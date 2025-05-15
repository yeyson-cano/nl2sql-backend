from dotenv import load_dotenv
load_dotenv()

import os
import uuid
import re
import io
import psycopg2
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.loaders.schema_loader import load_schema
from src.prompts.prompt_builder import load_schema_description, build_prompt
from src.sketcher.sql_sketcher import generate_sql_sketch
from src.clarifier.clarifier import find_placeholders, generate_followup_questions, apply_answer

app = FastAPI(title='Interactive NL2SQL')

# Able CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # o ["*"] para todos los orígenes (no recomendado en producción)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load once at startup
schema = load_schema()
schema_desc = load_schema_description()
conversation_store = {}

# --- Models ---

class SketchRequest(BaseModel):
    user_nl: str

class SketchResponse(BaseModel):
    conversation_id: str
    sql_sketch: str
    placeholders: list

class ClarifyRequest(BaseModel):
    conversation_id: str
    answer: str

class ClarifyResponse(BaseModel):
    sql_sketch: str
    next_question: str = None
    placeholders: list

class ExecuteResponse(BaseModel):
    rows: list
    total: int

# --- Helpers ---

def validate_sql(sql: str):
    """
    Stricter SQL validator: only allow a single SELECT statement without semicolons,
    comments, or dangerous keywords. Prevents SQL injection and multi-statement execution.
    """
    if not isinstance(sql, str):
        raise ValueError("SQL must be a string.")

    sql = sql.strip()
    upper = sql.upper()

    # Must start with SELECT
    if not upper.startswith("SELECT"):
        raise ValueError("Only SELECT statements are allowed.")

    # Disallow semicolons to prevent multiple statements
    if ";" in sql:
        raise ValueError("Semicolons are not allowed.")

    # Disallow comments
    if "--" in sql or "/*" in sql or "*/" in sql:
        raise ValueError("SQL comments are not allowed.")

    # Disallowed keywords
    forbidden_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE', 'MERGE']
    for keyword in forbidden_keywords:
        if re.search(r'\b' + keyword + r'\b', upper):
            raise ValueError(f"Disallowed keyword in SQL: {keyword}")

    # Optional: enforce basic structure
    if "FROM" not in upper:
        raise ValueError("SQL must contain a FROM clause.")

    return True

def execute_query(sql: str):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        dbname=os.getenv('DB_NAME')
    )
    with conn:
        with conn.cursor() as cur:
            # fetch sample
            cur.execute(sql + " LIMIT 5;")
            rows = cur.fetchall()
            # fetch total count
            count_sql = f"SELECT COUNT(*) FROM ({sql}) AS sub;"
            cur.execute(count_sql)
            total = cur.fetchone()[0]
    conn.close()
    return rows, total

def generate_excel(rows, columns):
    """
    Builds an in-memory Excel file from rows and column names.
    Returns a StreamingResponse.
    """
    df = pd.DataFrame(rows, columns=columns)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
    output.seek(0)
    return output

# --- Endpoints ---

@app.post('/sketch', response_model=SketchResponse)
def sketch(request: SketchRequest):
    conv_id = str(uuid.uuid4())
    prompt = build_prompt(request.user_nl, schema_desc)
    sql_sketch = generate_sql_sketch(prompt)
    placeholders = find_placeholders(sql_sketch)
    questions = generate_followup_questions(sql_sketch)
    conversation_store[conv_id] = {'sketch': sql_sketch, 'questions': questions}
    return SketchResponse(conversation_id=conv_id, sql_sketch=sql_sketch, placeholders=placeholders)

@app.post('/clarify', response_model=ClarifyResponse)
def clarify(request: ClarifyRequest):
    state = conversation_store.get(request.conversation_id)
    if not state:
        raise HTTPException(404, "Conversation not found")
    # get next placeholder
    questions = state['questions']
    if not questions:
        return ClarifyResponse(sql_sketch=state['sketch'], next_question=None, placeholders=[])
    ph, _ = questions.popitem()
    updated = apply_answer(state['sketch'], ph, request.answer)
    next_qs = generate_followup_questions(updated)
    state.update({'sketch': updated, 'questions': next_qs})
    next_question = list(next_qs.values())[0] if next_qs else None
    placeholders = list(next_qs.keys())
    return ClarifyResponse(sql_sketch=updated, next_question=next_question, placeholders=placeholders)

@app.get('/execute')
def execute(conversation_id: str = Query(...), as_excel: bool = Query(False)):
    state = conversation_store.get(conversation_id)
    if not state:
        raise HTTPException(404, "Conversation not found")
    sql = state['sketch']
    try:
        validate_sql(sql)
        rows, total = execute_query(sql)
    except ValueError as ve:
        print("[VALIDATION ERROR]", str(ve))
        raise HTTPException(400, str(ve))
    except psycopg2.OperationalError as oe:
        print("[DB CONNECTION ERROR]", str(oe))
        raise HTTPException(503, "Database unavailable")
    except Exception as e:
        print("[UNKNOWN ERROR]", str(e))
        raise HTTPException(500, str(e))

    if as_excel:
        # get column names from cursor description
        # We can re-execute a small query to get columns
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            dbname=os.getenv('DB_NAME')
        )
        with conn.cursor() as cur:
            cur.execute(sql + " LIMIT 0;")
            columns = [desc[0] for desc in cur.description]
        conn.close()
        output = generate_excel(rows, columns)
        return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                 headers={'Content-Disposition': 'attachment; filename="results.xlsx"'})
    else:
        return ExecuteResponse(rows=rows, total=total)
