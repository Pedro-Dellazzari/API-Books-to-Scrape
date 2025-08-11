#FASTAPI
from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer


#Modulos
#Banco de dados
from database.connection import get_connection

#API
from api.crud import get_generic_livros, get_livro_by_id, search_livros, get_all_categories, get_top_rated_books, get_books_by_price_range
from api.stats import get_overview_stats, get_category_stats
from api.health import check_health

#Auth
from auth.endpoints import router as auth_router

#Modelos Pydantic
from models.livros import Livro_Generico, Response_Livro_Generico, Response_Categories, HealthCheck, Response_Price_Range
from models.stats_responses import OverviewStats, CategoryStatsResponse

#typing
from typing import Annotated, Optional

#criando o app
app = FastAPI(title="API Books to Scrape", redirect_slashes=False)

#Incluindo routers
app.include_router(auth_router)

#Função health normal da API
@app.get("/health")
def healthcheck():
    return {"status": "Healthy"}

#Função health que vamos usar no banco de dados
@app.get("/healthdatabase")
def healthdatabase():
    try:
        conn = get_connection()
        result = conn.execute("SELECT * FROM livros LIMIT 1").fetchone()
        return {"status": "Healthy"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    

#ENDPOINT -- Retorna todos os livros dentro do banco de dados
@app.get("/api/v1/books", response_model=Response_Livro_Generico)
def listar_books(limit: int = Query(25, le=50), offset: int = Query(0, ge=0)):
    return get_generic_livros(limit=limit, offset=offset)

#ENDPOINT -- Retorna um livro específico pelo ID
@app.get("/api/v1/books/search", response_model=Response_Livro_Generico)
def search_books(
    title: Optional[str] = Query(None, description="Search by book title"),
    category: Optional[str] = Query(None, description="Search by book category"),
    limit: int = Query(25, le=50, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    return search_livros(title=title, category=category, limit=limit, offset=offset)

#ENDPOINT -- Retorna os livros mais bem avaliados
@app.get("/api/v1/books/top-rated", response_model=Response_Livro_Generico)
def top_rated_books(
    limit: int = Query(25, le=50, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    return get_top_rated_books(limit=limit, offset=offset)

#ENDPOINT -- Retorna livros por faixa de preço
@app.get("/api/v1/books/price-range", response_model=Response_Price_Range)
def books_by_price_range(
    min: Optional[float] = Query(None, description="Minimum price"),
    max: Optional[float] = Query(None, description="Maximum price"),
    currency: str = Query("euros", description="Currency: 'euros' or 'reais'"),
    limit: int = Query(25, le=50, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    return get_books_by_price_range(min_price=min, max_price=max, currency=currency, limit=limit, offset=offset)

#ENDPOINT -- Retorna um livro específico pelo ID
@app.get("/api/v1/books/{id}", response_model=Livro_Generico)
def buscar_book_por_id(id: str):
    livro = get_livro_by_id(id)
    if livro is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return livro

#ENDPOINT -- Retorna todas as categorias
@app.get("/api/v1/categories", response_model=Response_Categories)
def listar_categorias():
    return get_all_categories()

#ENDPOINT -- Health check da API e do banco de dados
@app.get("/api/v1/health", response_model=HealthCheck)
def health_check():
    return check_health()

#ENDPOINT -- Retorna estatísticas gerais da API
@app.get("/api/v1/stats/overview", response_model=OverviewStats)
def stats_overview():
    return get_overview_stats()

#ENDPOINT -- Retorna estatísticas por categoria
@app.get("/api/v1/stats/categories", response_model=CategoryStatsResponse)
def stats_categories():
    return get_category_stats()