from app.api import preprocess_tokens

def test_tokenization_and_pos():
    text = "Mostrar clientes con saldo mayor a 1000"
    tokens, pos = preprocess_tokens(text)

    # Que divida en al menos 6 tokens
    assert len(tokens) >= 6

    # Primer token "Mostrar" como VERB
    assert tokens[0] == "Mostrar"
    assert pos[0] == "VERB"

    # Número "1000" reconocido como NUM
    assert "1000" in tokens
    idx = tokens.index("1000")
    assert pos[idx] == "NUM"
