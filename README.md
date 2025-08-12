# 📚 API Books to Scrape

Uma API RESTful moderna para gerenciamento de livros com autenticação JWT, construída com FastAPI e PostgreSQL.

## 🎯 Visão Geral

Esta API fornece endpoints para consulta e pesquisa de livros, com recursos avançados de autenticação, filtragem por preços, categorias e avaliações. Ideal para sistemas de livrarias, e-commerce de livros ou aplicações de catalogação.

## 🏗️ Arquitetura

```
API Books to Scrape/
├── 📁 api/                    # Endpoints da API
│   ├── crud.py               # Operações CRUD de livros
│   ├── stats.py              # Endpoints de estatísticas
│   └── health.py             # Health checks
├── 📁 auth/                   # Sistema de autenticação
│   ├── endpoints.py          # Endpoints de autenticação
│   ├── jwt_handler.py        # Manipulação de tokens JWT
│   ├── database.py           # Operações de usuários
│   └── populate_users.py     # Script para popular usuários
├── 📁 database/               # Configuração do banco
│   ├── connection.py         # Conexão PostgreSQL
│   └── create_users_table.sql # Schema da tabela users
├── 📁 models/                 # Modelos Pydantic
│   ├── livros.py             # Modelos de livros
│   ├── auth.py               # Modelos de autenticação
│   └── stats_responses.py    # Modelos de estatísticas
├── 📁 books_data/            # Scripts de dados
│   └── loader_data.py        # Carregamento de dados
├── main.py                   # Aplicação principal
└── requirements.txt          # Dependências
```

## 🔧 Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **PostgreSQL** - Banco de dados relacional
- **JWT** - Autenticação baseada em tokens
- **Pydantic** - Validação de dados
- **bcrypt** - Hash seguro de senhas
- **psycopg2** - Driver PostgreSQL

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- PostgreSQL 12+
- Git


### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Configuração do Banco de Dados

Configure as variáveis de ambiente:

```bash
# .env
POSTGRES_ENDPOINT=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=books_scrape
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
JWT_SECRET_KEY=sua_chave_secreta_super_segura
```

### 3. Execute o script de população de usuários

```bash
cd auth
python3 populate_users.py
```

### 4. Inicie a aplicação

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

A API estará disponível em: `http://localhost:8000`

📖 **Documentação interativa:** `http://localhost:8000/docs`

## 🔐 Autenticação

### Sistema JWT

A API utiliza autenticação JWT com dois tipos de tokens:

- **Access Token**: Validade de 30 minutos, usado para acessar endpoints
- **Refresh Token**: Validade de 7 dias, usado para renovar access tokens

### Usuários Padrão

Após executar o script `populate_users.py`:

- **Admin**: `username: admin`, `password: admin123`
- **Usuários**: `username: [qualquer_username]`, `password: senha123`

## 📋 Documentação das Rotas

### 🔓 Endpoints Públicos

#### Health Checks
```http
GET /health                 # Health simples
GET /healthdatabase        # Health do banco
GET /api/v1/health         # Health completo da API
```

### 🔐 Autenticação

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Renovar Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Perfil do Usuário
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### 📚 Endpoints de Livros (Autenticação Obrigatória)

Todos os endpoints abaixo requerem header de autorização:
```http
Authorization: Bearer <access_token>
```

#### Listar Todos os Livros
```http
GET /api/v1/books?limit=25&offset=0
```

**Response:**
```json
{
  "limit": 25,
  "offset": 0,
  "has_more": true,
  "results_returned": 25,
  "books": [
    {
      "upc_livro": "a897fe39b1053632",
      "titulo": "A Light in the Attic",
      "categoria": "Poetry",
      "valor_principal_em_euros": 51.77,
      "valor_principal_em_reais": 289.74,
      "review": "Three",
      "link": "http://books.toscrape.com/catalogue/..."
    }
  ]
}
```

#### Buscar Livros
```http
GET /api/v1/books/search?title=light&category=poetry&limit=10&offset=0
```

#### Livros Mais Bem Avaliados
```http
GET /api/v1/books/top-rated?limit=10&offset=0
```

#### Livros por Faixa de Preço
```http
GET /api/v1/books/price-range?min=10&max=50&currency=euros&limit=20
```

**Response:**
```json
{
  "limit": 20,
  "offset": 0,
  "has_more": false,
  "results_returned": 15,
  "filter_currency": "euros",
  "min_price": 10,
  "max_price": 50,
  "books": [...]
}
```

#### Livro Específico
```http
GET /api/v1/books/{upc_livro}
```

#### Listar Categorias
```http
GET /api/v1/categories
```

**Response:**
```json
{
  "categories": [
    "Travel",
    "Mystery",
    "Historical Fiction",
    "Sequential Art"
  ],
  "total_categories": 50
}
```

### 📊 Endpoints de Estatísticas

#### Estatísticas Gerais
```http
GET /api/v1/stats/overview
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "total_books": 1000,
  "total_categories": 50,
  "average_price_euros": 35.26,
  "average_price_reais": 197.21,
  "most_expensive_book": {
    "titulo": "The Requiem Red",
    "valor_principal_em_euros": 22.65
  },
  "cheapest_book": {
    "titulo": "The Coming Woman",
    "valor_principal_em_euros": 17.93
  }
}
```

#### Estatísticas por Categoria
```http
GET /api/v1/stats/categories
Authorization: Bearer <access_token>
```

## 📝 Exemplos de Uso

### Fluxo Completo de Autenticação

```bash
# 1. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# 2. Usar o token retornado
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# 3. Acessar endpoints protegidos
curl -X GET "http://localhost:8000/api/v1/books" \
  -H "Authorization: Bearer $TOKEN"

# 4. Buscar livros específicos
curl -X GET "http://localhost:8000/api/v1/books/search?title=python" \
  -H "Authorization: Bearer $TOKEN"
```

### Exemplo com Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "admin", "password": "admin123"}
)
tokens = response.json()

# Headers para requisições autenticadas
headers = {
    "Authorization": f"Bearer {tokens['access_token']}"
}

# Buscar livros
books = requests.get(
    "http://localhost:8000/api/v1/books",
    headers=headers,
    params={"limit": 10}
)

print(books.json())
```

### Exemplo com JavaScript

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});

const tokens = await loginResponse.json();

// Buscar livros
const booksResponse = await fetch('http://localhost:8000/api/v1/books?limit=5', {
  headers: {
    'Authorization': `Bearer ${tokens.access_token}`
  }
});

const books = await booksResponse.json();
console.log(books);
```

## ⚡ Execução

### Desenvolvimento
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Produção
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

```


## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de conexão com banco**
   - Verifique as variáveis de ambiente
   - Confirme se o PostgreSQL está rodando

2. **Token expirado**
   - Use o refresh token para obter um novo access token
   - Implemente renovação automática no frontend

3. **Erro 307 (Redirect)**
   - Já corrigido com `redirect_slashes=False`

