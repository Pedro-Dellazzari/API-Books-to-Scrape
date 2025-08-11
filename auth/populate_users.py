#!/usr/bin/env python3
"""
Script para popular a tabela users com dados fictícios e uma conta admin.
Execute este script após criar a tabela users no PostgreSQL.
"""

import sys
import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()
import os

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.jwt_handler import get_password_hash


def get_connection():
    """Retorna uma conexão com PostgreSQL"""
    connection_params = {
        'host': os.getenv('POSTGRES_ENDPOINT'),
        'port': os.getenv('POSTGRES_PORT'),
        'database': os.getenv('POSTGRES_DATABASE'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD')
    }
    
    conn = psycopg2.connect(**connection_params)
    return conn


def create_users_table():
    """Cria a tabela users se ela não existir"""
    with open("database/create_users_table.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql_script)
        conn.commit()
        print("✓ Tabela users criada com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabela users: {e}")
        conn.rollback()
    finally:
        conn.close()

def populate_users():
    """Popula a tabela users com dados fictícios"""
    users_data = [
        {
            "username": "admin",
            "email": "admin@bookstore.com",
            "full_name": "Administrador do Sistema",
            "password": "admin123",
            "is_admin": True
        },
        {
            "username": "joao.silva",
            "email": "joao.silva@email.com",
            "full_name": "João Silva",
            "password": "senha123",
            "is_admin": False
        },
        {
            "username": "maria.santos",
            "email": "maria.santos@email.com",
            "full_name": "Maria Santos",
            "password": "senha123",
            "is_admin": False
        },
        {
            "username": "pedro.oliveira",
            "email": "pedro.oliveira@email.com",
            "full_name": "Pedro Oliveira",
            "password": "senha123",
            "is_admin": False
        },
        {
            "username": "ana.costa",
            "email": "ana.costa@email.com",
            "full_name": "Ana Costa",
            "password": "senha123",
            "is_admin": False
        },
        {
            "username": "carlos.ferreira",
            "email": "carlos.ferreira@email.com",
            "full_name": "Carlos Ferreira",
            "password": "senha123",
            "is_admin": False
        },
        {
            "username": "lucia.rodrigues",
            "email": "lucia.rodrigues@email.com",
            "full_name": "Lucia Rodrigues",
            "password": "senha123",
            "is_admin": False
        },
        {
            "username": "rafael.mendes",
            "email": "rafael.mendes@email.com",
            "full_name": "Rafael Mendes",
            "password": "senha123",
            "is_admin": False
        },
        {
            "username": "patricia.alves",
            "email": "patricia.alves@email.com",
            "full_name": "Patricia Alves",
            "password": "senha123",
            "is_admin": False
        },
        {
            "username": "ricardo.lima",
            "email": "ricardo.lima@email.com",
            "full_name": "Ricardo Lima",
            "password": "senha123",
            "is_admin": False
        }
    ]

    sql = """
        INSERT INTO users (username, email, full_name, hashed_password, is_admin)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING
    """
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        created_count = 0
        for user_data in users_data:
            hashed_password = get_password_hash(user_data["password"])
            cursor.execute(sql, (
                user_data["username"],
                user_data["email"],
                user_data["full_name"],
                hashed_password,
                user_data["is_admin"]
            ))
            if cursor.rowcount > 0:
                created_count += 1
        
        conn.commit()
        print(f"✓ {created_count} usuários criados com sucesso!")
        
        # Lista os usuários criados
        cursor.execute("SELECT username, email, full_name, is_admin FROM users ORDER BY id")
        users = cursor.fetchall()
        
        print("\n📋 Usuários na base de dados:")
        print("-" * 80)
        print(f"{'Username':<20} {'Email':<25} {'Nome Completo':<25} {'Admin':<5}")
        print("-" * 80)
        for user in users:
            admin_status = "✓" if user[3] else "✗"
            print(f"{user[0]:<20} {user[1]:<25} {user[2] or 'N/A':<25} {admin_status:<5}")
        
        print(f"\n🔑 Credenciais de acesso:")
        print("Admin: username='admin', password='admin123'")
        print("Usuários: username='[qualquer_username]', password='senha123'")
        
    except Exception as e:
        print(f"❌ Erro ao popular tabela users: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🚀 Inicializando população da tabela users...")
    
    try:
        # Cria a tabela se não existir
        create_users_table()
        
        # Popula com dados fictícios
        populate_users()
        
        print("\n✅ Script executado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)