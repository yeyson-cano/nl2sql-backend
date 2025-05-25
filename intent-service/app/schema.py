from pydantic import BaseModel, Field
from typing import List, Optional


class IntentRequest(BaseModel):
    """
    Modelo de petición para el endpoint /api/intent.
    Contiene el texto en lenguaje natural que se desea analizar.
    """
    text: str = Field(..., description="Consulta en lenguaje natural del usuario")


class Predicate(BaseModel):
    """
    Representa un predicado extraído de la consulta:
    una condición de filtrado sobre una columna.
    """
    column: str = Field(..., description="Nombre completo de la columna (incluye tabla si aplica)")
    operator: str = Field(..., description="Operador de comparación ('=', '>', '<', 'BETWEEN', etc.)")
    value: str = Field(..., description="Valor asociado al predicado")


class IntentResponse(BaseModel):
    """
    Modelo de respuesta del endpoint /api/intent.
    Incluye listas de los distintos elementos identificados.
    """
    entities: List[str] = Field(
        ..., description="Lista de tablas y columnas reconocidas en la consulta"
    )
    predicates: List[Predicate] = Field(
        default_factory=list,
        description="Lista de condiciones de filtrado extraídas"
    )
    aggregations: List[str] = Field(
        default_factory=list,
        description="Funciones de agregación detectadas (p.ej. 'SUM(monto)')"
    )
    groupings: List[str] = Field(
        default_factory=list,
        description="Columnas indicadas para agrupar (cláusula GROUP BY)"
    )
    # Puedes añadir más campos si luego detectas necesidad (p. ej. order_by, limit, etc.)


# Para facilitar la documentación automática de FastAPI:
#   - Los Field(...) añaden descripciones que aparecerán en /docs
#   - Las listas vacías por defecto evitan problemas si no se encuentran elementos
