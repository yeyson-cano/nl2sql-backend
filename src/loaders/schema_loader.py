import os
import json
import psycopg2
from dotenv import load_dotenv

def load_schema():
    # Load environment variables
    load_dotenv()
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "user"),
        password=os.getenv("DB_PASS", "pass"),
        dbname=os.getenv("DB_NAME", "testdb"),
    )
    cursor = conn.cursor()

    # Fetch all public tables
    cursor.execute(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public';
        """
    )
    tables = [r[0] for r in cursor.fetchall()]

    # Fetch columns/types for each table
    schema = {}
    for table in tables:
        cursor.execute(
            f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table}';
            """
        )
        schema[table] = cursor.fetchall()

    conn.close()

    # Ensure data directory exists
    data_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    )
    os.makedirs(data_dir, exist_ok=True)
    out_path = os.path.join(data_dir, 'schema.json')

    # Dump schema to JSON
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    return schema

if __name__ == '__main__':
    schema = load_schema()
    print('Schema loaded and saved to data/schema.json')