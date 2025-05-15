import pytest
from src.clarifier.clarifier import (
    find_placeholders,
    generate_question,
    generate_followup_questions,
    apply_answer,
    apply_all_answers
)

@pytest.fixture
def sample_sketch():
    return "SELECT [COLUMNS] FROM [TABLE] WHERE [CONDITION];"

def test_find_placeholders(sample_sketch):
    assert find_placeholders(sample_sketch) == ['COLUMNS', 'TABLE', 'CONDITION']

@pytest.mark.parametrize("ph,expected", [
    ('COLUMNS', 'Which columns would you like to select?'),
    ('TABLE', 'Which table would you like to query?'),
    ('CONDITION', 'What filter condition should be applied?'),
    ('UNKNOWN', 'Please specify the value for unknown.')
])
def test_generate_question(ph, expected):
    assert generate_question(ph) == expected

def test_generate_followup_questions(sample_sketch):
    questions = generate_followup_questions(sample_sketch)
    assert questions['COLUMNS'].startswith('Which columns')
    assert 'TABLE' in questions

def test_apply_answer_numeric():
    sketch = "WHERE [CONDITION]"
    result = apply_answer(sketch, 'CONDITION', '100')
    assert result == 'WHERE 100'

def test_apply_answer_text():
    sketch = "FROM [TABLE]"
    result = apply_answer(sketch, 'TABLE', 'sales')
    assert result == "FROM 'sales'"

def test_apply_all_answers(sample_sketch):
    answers = {
        'COLUMNS': 'id, name',
        'TABLE': 'users',
        'CONDITION': 'age > 18'
    }
    final = apply_all_answers(sample_sketch, answers)
    expected = "SELECT 'id, name' FROM 'users' WHERE 'age > 18';"
    assert final == expected