import re
from typing import List, Dict

# Mapping of placeholders to clarification questions
PLACEHOLDER_QUESTIONS: Dict[str, str] = {
    'COLUMNS': 'Which columns would you like to select?',
    'TABLE':   'Which table would you like to query?',
    'CONDITION': 'What filter condition should be applied?'
}


def find_placeholders(sql_sketch: str) -> List[str]:
    """
    Detects and returns a list of unique placeholders in the SQL sketch.
    Placeholders are denoted by [PLACEHOLDER].
    """
    tokens = re.findall(r"\[([A-Z_]+)\]", sql_sketch)
    seen = set()
    unique_tokens = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            unique_tokens.append(t)
    return unique_tokens


def generate_question(placeholder: str) -> str:
    """
    Returns a clarification question for a given placeholder.
    If no specific question is defined, returns a generic one.
    """
    return PLACEHOLDER_QUESTIONS.get(
        placeholder,
        f'Please specify the value for {placeholder.lower()}.'
    )


def generate_followup_questions(sql_sketch: str) -> Dict[str, str]:
    """
    For a given SQL sketch, returns a dict mapping each placeholder
    to its clarification question.
    """
    placeholders = find_placeholders(sql_sketch)
    return {ph: generate_question(ph) for ph in placeholders}


def apply_answer(sql_sketch: str, placeholder: str, answer: str) -> str:
    """
    Replaces all occurrences of the placeholder with the answer.
    Non-numeric answers are wrapped in single quotes.
    """
    formatted = answer
    if not re.fullmatch(r"[-+]?\d+(\.\d+)?", answer):
        formatted = f"'{answer}'"
    pattern = re.compile(rf"\[{re.escape(placeholder)}\]")
    return pattern.sub(formatted, sql_sketch)


def apply_all_answers(sql_sketch: str, answers: Dict[str, str]) -> str:
    """
    Applies multiple placeholder answers in sequence.
    """
    updated = sql_sketch
    for ph, ans in answers.items():
        updated = apply_answer(updated, ph, ans)
    return updated
