from database.connection import get_connection
from models.auth import User, UserCreate
from auth.jwt_handler import get_password_hash, verify_password
from typing import Optional
import psycopg2.extras

def create_user(user_data: UserCreate) -> Optional[User]:
    """Cria um novo usuário no banco de dados"""
    hashed_password = get_password_hash(user_data.password)
    
    sql = """
        INSERT INTO users (username, email, full_name, hashed_password)
        VALUES (%s, %s, %s, %s)
        RETURNING id, username, email, full_name, is_active, is_admin, created_at
    """
    
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, (
            user_data.username,
            user_data.email,
            user_data.full_name,
            hashed_password
        ))
        result = cursor.fetchone()
        conn.commit()
        
        if result:
            return User(**dict(result))
        return None
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_user_by_username(username: str) -> Optional[User]:
    """Busca um usuário pelo username"""
    sql = """
        SELECT id, username, email, full_name, is_active, is_admin, created_at
        FROM users
        WHERE username = %s AND is_active = TRUE
    """
    
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        
        if result:
            return User(**dict(result))
        return None
        
    finally:
        conn.close()

def get_user_by_id(user_id: int) -> Optional[User]:
    """Busca um usuário pelo ID"""
    sql = """
        SELECT id, username, email, full_name, is_active, is_admin, created_at
        FROM users
        WHERE id = %s AND is_active = TRUE
    """
    
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        
        if result:
            return User(**dict(result))
        return None
        
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Autentica um usuário verificando username e senha"""
    sql = """
        SELECT id, username, email, full_name, is_active, is_admin, created_at, hashed_password
        FROM users
        WHERE username = %s AND is_active = TRUE
    """
    
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        
        if not result:
            return None
            
        # Verifica a senha
        if not verify_password(password, result['hashed_password']):
            return None
            
        # Remove a senha do resultado antes de retornar
        user_data = dict(result)
        del user_data['hashed_password']
        
        return User(**user_data)
        
    finally:
        conn.close()

def user_exists(username: str, email: str) -> bool:
    """Verifica se já existe um usuário com o mesmo username ou email"""
    sql = """
        SELECT COUNT(*) as count
        FROM users
        WHERE username = %s OR email = %s
    """
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (username, email))
        result = cursor.fetchone()
        return result[0] > 0
        
    finally:
        conn.close()