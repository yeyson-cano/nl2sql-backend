import os
import json

def load_schema_description(path=None) -> str:
    """
    Build a human-readable description of the DB schema for prompts.
    """
    if path is None:
        base = os.path.dirname(__file__)
        path = os.path.abspath(
            os.path.join(base, '..', '..', 'data', 'schema.json')
        )
    with open(path, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    lines = ['Available tables:']
    for table, cols in schema.items():
        desc = ', '.join(f"{col} ({dtype})" for col, dtype in cols)
        lines.append(f"- {table}: {desc}")
    return '\n'.join(lines)


def build_prompt(user_request: str, schema_desc: str) -> str:
    """
    Combine schema description and user request into an LLM prompt,
    instructing it to generate a single SELECT statement without a trailing semicolon.
    """
    return (
        f"Database schema:\n{schema_desc}\n\n"
        "Generate one SQL SELECT statement only, without a trailing semicolon, "
        "and do not include any other SQL commands. Use placeholders where needed.\n"
        f"User request: {user_request}\n\n"
        "Expected output format (placeholders):\n"
        "SELECT [COLUMNS]\n"
        "FROM [TABLE]\n"
        "WHERE [CONDITION]"
    )

if __name__ == '__main__':
    desc = load_schema_description()
    prompt_text = build_prompt('Show total sales by region', desc)
    print(prompt_text)
