#Importando bibliotecas 
from database.connection import get_connection
from typing import Dict, Any
import psycopg2.extras


def get_overview_stats() -> Dict[str, Any]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Total de livros
        cursor.execute("SELECT COUNT(*) FROM livros")
        total_books_result = cursor.fetchone()
        total_books = total_books_result[0] if total_books_result else 0
        
        # Preço médio em euros
        cursor.execute("SELECT AVG(valor_principal_em_euros) FROM livros WHERE valor_principal_em_euros > 0")
        avg_price_result = cursor.fetchone()
        avg_price_euros = round(avg_price_result[0], 2) if avg_price_result[0] else 0.0
        
        # Preço médio em reais
        cursor.execute("SELECT AVG(valor_principal_em_reais) FROM livros WHERE valor_principal_em_reais > 0")
        avg_price_reais_result = cursor.fetchone()
        avg_price_reais = round(avg_price_reais_result[0], 2) if avg_price_reais_result[0] else 0.0
        
        # Distribuição de ratings
        cursor.execute("""
            SELECT 
                review,
                COUNT(*) as count
            FROM livros 
            WHERE review IS NOT NULL AND review != ''
            GROUP BY review
            ORDER BY review
        """)
        ratings_distribution = cursor.fetchall()
        ratings_dict = {row[0]: row[1] for row in ratings_distribution}
        
        # Categorias mais populares
        cursor.execute("""
            SELECT 
                categoria,
                COUNT(*) as count
            FROM livros 
            WHERE categoria IS NOT NULL AND categoria != ''
            GROUP BY categoria
            ORDER BY count DESC
            LIMIT 5
        """)
        top_categories = cursor.fetchall()
        top_categories_list = [{"category": row[0], "count": row[1]} for row in top_categories]
        
        return {
            "total_books": total_books,
            "average_price_euros": avg_price_euros,
            "average_price_reais": avg_price_reais,
            "ratings_distribution": ratings_dict,
            "top_categories": top_categories_list
        }
    finally:
        conn.close()


def get_category_stats() -> Dict[str, Any]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                categoria,
                COUNT(*) as total_books,
                AVG(valor_principal_em_euros) as avg_price_euros,
                MIN(valor_principal_em_euros) as min_price_euros,
                MAX(valor_principal_em_euros) as max_price_euros,
                AVG(valor_principal_em_reais) as avg_price_reais,
                MIN(valor_principal_em_reais) as min_price_reais,
                MAX(valor_principal_em_reais) as max_price_reais
            FROM livros 
            WHERE categoria IS NOT NULL AND categoria != ''
            GROUP BY categoria
            ORDER BY total_books DESC
        """)
        category_stats = cursor.fetchall()
        
        categories_data = []
        for row in category_stats:
            categories_data.append({
                "category": row[0],
                "total_books": row[1],
                "avg_price_euros": round(row[2], 2) if row[2] else 0.0,
                "min_price_euros": round(row[3], 2) if row[3] else 0.0,
                "max_price_euros": round(row[4], 2) if row[4] else 0.0,
                "avg_price_reais": round(row[5], 2) if row[5] else 0.0,
                "min_price_reais": round(row[6], 2) if row[6] else 0.0,
                "max_price_reais": round(row[7], 2) if row[7] else 0.0
            })
        
        return {
            "categories": categories_data,
            "total_categories": len(categories_data)
        }
    finally:
        conn.close()