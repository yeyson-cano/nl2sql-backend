# intent-service/app/model.py

import spacy
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# 1. spaCy para tokenización y POS
nlp_spacy = spacy.load("es_core_news_sm")

# 2. BERT NER pipeline
#    - tokenizer y modelo finetuneado sobre Spider
#    - ajusta el nombre al tuyo si has subido tu checkpoint; 
#      aquí usamos 'bert-base-uncased' como placeholder y 
#      asumimos que ya lo fine-tuneaste y subiste a HF hub o ruta local.
TOKENIZER_NAME = "bert-base-uncased"
MODEL_NAME     = "path/to/tu-bert-finetuned-spider"

tokenizer_ner = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
model_ner     = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)

nlp_ner = pipeline(
    "ner",
    model=model_ner,
    tokenizer=tokenizer_ner,
    aggregation_strategy="simple"  # agrupa subtokens
)
