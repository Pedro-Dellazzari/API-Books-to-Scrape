#Importando bibliotecas
from pydantic import BaseModel
from typing import List

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