#Importando bibliotecas 
from database.connection import get_connection
from typing import Dict, Any


def check_health() -> Dict[str, Any]:
    api_status = "healthy"
    database_status = "healthy"
    database_message = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Tenta uma query simples na tabela principal
        cursor.execute("SELECT COUNT(*) FROM livros")
        result = cursor.fetchone()
        if result is None:
            database_status = "unhealthy"
            database_message = "Database query returned no result"
        else:
            database_message = f"Database connection successful. Found {result[0]} books in total."
        conn.close()
    except Exception as e:
        database_status = "unhealthy"
        database_message = f"Database connection failed: {str(e)}"
    
    return {
        "api_status": api_status,
        "database_status": database_status,
        "database_message": database_message
    }