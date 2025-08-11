#Importando bibliotecas 
from database.connection import get_connection
from models.livros import Livro_Generico
from typing import Dict, Any
import psycopg2.extras


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
        LIMIT %s OFFSET %s
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, (limit, offset))
        rows = cursor.fetchall()
        
        livros = [Livro_Generico(**dict(row)) for row in rows]
        
        return {
            "limit": limit,
            "offset": offset,
            "has_more": len(livros) == limit,
            "results_returned": len(livros),
            "books": [livro.model_dump() for livro in livros],
        }
    finally:
        conn.close()

#Função para buscar um livro específico pelo ID
def get_livro_by_id(livro_id: str) -> Dict[str, Any]:
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
        WHERE upc_livro = %s
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, (livro_id,))
        result = cursor.fetchone()
        
        if result is None:
            return None
        
        livro = Livro_Generico(**dict(result))
        return livro.model_dump()
    finally:
        conn.close()

#Função para buscar livros com filtros de título e categoria
def search_livros(title: str = None, category: str = None, limit: int = 25, offset: int = 0) -> Dict[str, Any]:
    conditions = []
    params = []
    
    if title:
        conditions.append("titulo ILIKE %s")
        params.append(f"%{title}%")
    
    if category:
        conditions.append("categoria ILIKE %s")
        params.append(f"%{category}%")
    
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
    
    sql = f"""
        SELECT
            upc_livro,
            titulo,
            categoria,
            valor_principal_em_euros,
            valor_principal_em_reais,
            review,
            link
        FROM livros
        {where_clause}
        ORDER BY titulo
        LIMIT %s OFFSET %s
    """
    
    params.extend([limit, offset])
    
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        livros = [Livro_Generico(**dict(row)) for row in rows]
        
        return {
            "limit": limit,
            "offset": offset,
            "has_more": len(livros) == limit,
            "results_returned": len(livros),
            "books": [livro.model_dump() for livro in livros],
        }
    finally:
        conn.close()

#Função para retornar todas as categorias
def get_all_categories() -> Dict[str, Any]:
    sql = """
        SELECT DISTINCT categoria
        FROM livros
        WHERE categoria IS NOT NULL AND categoria != ''
        ORDER BY categoria
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        
        categories = [row[0] for row in result]
        
        return {
            "categories": categories,
            "total_categories": len(categories)
        }
    finally:
        conn.close()


#Função para retornar os livros mais bem avaliados
def get_top_rated_books(limit: int = 25, offset: int = 0) -> Dict[str, Any]:
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
        WHERE review IS NOT NULL AND review != ''
        ORDER BY 
            CASE review
                WHEN 'Five' THEN 5
                WHEN 'Four' THEN 4
                WHEN 'Three' THEN 3
                WHEN 'Two' THEN 2
                WHEN 'One' THEN 1
                ELSE 0
            END DESC,
            titulo ASC
        LIMIT %s OFFSET %s
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, (limit, offset))
        rows = cursor.fetchall()
        
        livros = [Livro_Generico(**dict(row)) for row in rows]
        
        return {
            "limit": limit,
            "offset": offset,
            "has_more": len(livros) == limit,
            "results_returned": len(livros),
            "books": [livro.model_dump() for livro in livros],
        }
    finally:
        conn.close()

#Função para buscar livros por faixa de preço
def get_books_by_price_range(min_price: float = None, max_price: float = None, currency: str = "euros", limit: int = 25, offset: int = 0) -> Dict[str, Any]:
    conditions = []
    params = []
    
    # Determina qual coluna de preço usar
    price_column = "valor_principal_em_euros" if currency == "euros" else "valor_principal_em_reais"
    
    if min_price is not None:
        conditions.append(f"{price_column} >= %s")
        params.append(min_price)
    
    if max_price is not None:
        conditions.append(f"{price_column} <= %s")
        params.append(max_price)
    
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
    
    sql = f"""
        SELECT
            upc_livro,
            titulo,
            categoria,
            valor_principal_em_euros,
            valor_principal_em_reais,
            review,
            link
        FROM livros
        {where_clause}
        ORDER BY {price_column} ASC, titulo ASC
        LIMIT %s OFFSET %s
    """
    
    params.extend([limit, offset])
    
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        livros = [Livro_Generico(**dict(row)) for row in rows]
        
        return {
            "limit": limit,
            "offset": offset,
            "has_more": len(livros) == limit,
            "results_returned": len(livros),
            "books": [livro.model_dump() for livro in livros],
            "filter_currency": currency,
            "min_price": min_price,
            "max_price": max_price
        }
    finally:
        conn.close()