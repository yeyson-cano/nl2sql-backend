from pydantic import BaseModel
from typing import List

class IntentRequest(BaseModel):
    text: str

class IntentResponse(BaseModel):
    entidades: List[str]
    predicados: List[dict]
    agregaciones: List[str]
    agrupamientos: List[str]
