from fastapi import APIRouter, HTTPException
from .schema import IntentRequest, IntentResponse
from .model import nlp_spacy  # Tokenización y POS
# from .model import nlp_ner  # Pipeline NER, cuando lo implementes

router = APIRouter()

def preprocess_tokens(text: str):
    """
    Tokeniza el texto y corrige etiquetas POS para tokens puramente numéricos.
    Retorna listas de tokens y etiquetas POS corregidas.
    """
    doc = nlp_spacy(text)
    tokens = []
    pos_tags = []
    for token in doc:
        lbl = token.pos_
        # Corrección: si es un dígito puro y spaCy lo marcó como NOUN, reasignar a NUM
        if token.text.isdigit() and lbl == "NOUN":
            lbl = "NUM"
        tokens.append(token.text)
        pos_tags.append(lbl)
    return tokens, pos_tags

@router.post("/api/intent", response_model=IntentResponse)
def extract_intent(req: IntentRequest):
    """
    Endpoint para analizar la intención de la consulta en lenguaje natural.
    - Tokeniza y hace POS tagging con corrección de etiquetas numéricas.
    - (Más adelante) extrae entidades, predicados, agregaciones y agrupamientos.
    """
    # 1. Tokenización y POS tagging con corrección
    try:
        tokens, pos_tags = preprocess_tokens(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en spaCy: {e}")

    # (Opcional) registrar en log para depuración:
    # logger.debug(f"Tokens: {tokens}")
    # logger.debug(f"POS tags: {pos_tags}")

    # 2. (Placeholder) Lógica de extracción NER / entidades
    #    Aquí usaremos nlp_ner(req.text) cuando esté implementado.
    entities = []       # sustituir por la lista real
    predicates = []     # sustituir por la lista real
    aggregations = []   # sustituir por la lista real
    groupings = []      # sustituir por la lista real

    # 3. Construcción de la respuesta
    return IntentResponse(
        entities=entities,
        predicates=predicates,
        aggregations=aggregations,
        groupings=groupings
    )
