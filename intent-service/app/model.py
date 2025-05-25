# intent-service/app/model.py

import spacy

# Carga del modelo de spaCy para español
# (asegúrate de haber instalado es_core_news_sm)
nlp_spacy = spacy.load("es_core_news_sm")
