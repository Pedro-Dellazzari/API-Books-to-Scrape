#Importando bibliotecas 
from database.connection import get_connection
from models.livros import Livro_Generico
from typing import Dict, Any


#Função padrão para retornar todos os livros sem filtros
def get_generic_livros(limit: int = 25, offset: int = 0) -> Dict[str, Any]:
    sql = """
        SELECT
            upc_livro,
            titulo,
            categoria,
            valor_principal_em_euros,
            valor_principal_em_reais,
            review,
            link
        FROM livros
        ORDER BY titulo
        LIMIT ? OFFSET ?
    """
    with get_connection() as conn:
        df = conn.execute(sql, [limit, offset]).fetchdf()

    livros = [Livro_Generico(**row._asdict()) for row in df.itertuples(index=False)]
    
    return {
        "limit": limit,
        "offset": offset,
        "has_more": len(livros) == limit,
        "results_returned": len(livros),
        "books": [livro.model_dump() for livro in livros],  # Corrigido para lista
    }