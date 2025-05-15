import re


def extract_sql(raw_response: str) -> str:
    """
    Extracts the first SQL SELECT statement from the raw LLM response.
    Strips trailing semicolons and whitespace.

    Args:
        raw_response: The full text returned by the LLM.

    Returns:
        A clean SQL string starting with SELECT.

    Raises:
        ValueError: If no valid SELECT statement is found.
    """
    # Regex to capture SELECT ... up to first semicolon or end of string
    match = re.search(r"(SELECT[\s\S]+?)(;|$)", raw_response, re.IGNORECASE)
    if not match:
        raise ValueError("No valid SELECT statement found in model response.")
    sql = match.group(1).strip()
    return sql