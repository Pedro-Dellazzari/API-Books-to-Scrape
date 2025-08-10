#Importando bibliotecas 
from database.connection import get_connection
from models.livros import Livro_Generico
from typing import Dict, Any


#Função padrão para retornar todos os livros sem filtros
def get_generic_livros(limit: int = 25, offset: int = 0) -> Dict[str, Any]:
    conn = get_connection()

    query = f"""
        SELECT * FROM livros
        ORDER BY titulo
        LIMIT {limit} OFFSET {offset}
    """

    # 🔄 Retorna DataFrame diretamente
    df = conn.execute(query).fetchdf()
    conn.close()

    # 🧱 Transforma linha por linha do DataFrame em objetos Livro
    livros = [Livro_Generico(**row._asdict()) for row in df.itertuples(index=False)]

    response = {
        "limit": limit,
        "offset": offset,
        "has_more": len(livros) == limit,
        "results_returned": len(livros),
        "books": livros
    }

    return response
