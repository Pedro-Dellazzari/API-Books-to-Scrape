#Importando bibliotecas
from pydantic import BaseModel
from typing import List, Optional, Dict
from models.livros import Livro_Generico


class CategoryCount(BaseModel):
    category: str
    count: int


class OverviewStats(BaseModel):
    total_books: int
    average_price_euros: float
    average_price_reais: float
    ratings_distribution: Dict[str, int]
    top_categories: List[CategoryCount]


class CategoryStats(BaseModel):
    category: str
    total_books: int
    avg_price_euros: float
    min_price_euros: float
    max_price_euros: float
    avg_price_reais: float
    min_price_reais: float
    max_price_reais: float


class CategoryStatsResponse(BaseModel):
    categories: List[CategoryStats]
    total_categories: int