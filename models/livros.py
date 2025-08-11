#Importando bibliotecas
from pydantic import BaseModel
from typing import List, Optional

class Livro_Generico(BaseModel):
    upc_livro: str
    titulo: str
    categoria: str
    valor_principal_em_euros: float
    valor_principal_em_reais: float
    review: str
    link: str


class Response_Livro_Generico(BaseModel):
    limit: int
    offset: int
    has_more:bool
    results_returned: int
    books: List[Livro_Generico]


class Response_Categories(BaseModel):
    categories: List[str]
    total_categories: int


class HealthCheck(BaseModel):
    api_status: str
    database_status: str
    database_message: Optional[str] = None


class Response_Price_Range(BaseModel):
    limit: int
    offset: int
    has_more: bool
    results_returned: int
    books: List[Livro_Generico]
    filter_currency: str
    min_price: Optional[float]
    max_price: Optional[float]