#Importando bibliotecas
from pydantic import BaseModel

class Livro_Generico(BaseModel):
    upc_livro: str
    titulo: str
    categoria: str
    valor_principal_em_euros: float
    valor_principal_em_reais: float
    review: str
    link: str