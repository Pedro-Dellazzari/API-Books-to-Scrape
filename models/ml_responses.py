from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class BookFeature(BaseModel):
    """Modelo para features de um livro processado para ML"""
    upc_livro: str
    titulo_length: int
    categoria_encoded: int
    preco_euros_normalized: float
    preco_reais_normalized: float
    review_score: int
    titulo_word_count: int
    categoria: str
    has_discount: bool
    price_category: str

class MLFeatures(BaseModel):
    """Response para endpoint de features"""
    total_records: int
    feature_columns: List[str]
    categorical_mappings: Dict[str, Dict[str, int]]
    normalization_stats: Dict[str, Dict[str, float]]
    features: List[BookFeature]
    metadata: Dict[str, Any]

class TrainingRecord(BaseModel):
    """Registro individual para training dataset"""
    upc_livro: str
    titulo: str
    categoria: str
    preco_euros: float
    preco_reais: float
    review: Optional[str]
    titulo_length: int
    titulo_word_count: int
    categoria_encoded: int
    preco_euros_normalized: float
    preco_reais_normalized: float
    review_score: int
    has_discount: bool
    price_category: str
    target_popular: bool  # Target variable - se o livro é popular baseado em algum critério

class TrainingDataset(BaseModel):
    """Response para endpoint de training data"""
    total_records: int
    train_test_split_info: Dict[str, Any]
    feature_descriptions: Dict[str, str]
    target_variable: str
    data: List[TrainingRecord]
    statistics: Dict[str, Any]
    created_at: datetime

class MLStats(BaseModel):
    """Estatísticas gerais para ML"""
    total_books: int
    total_categories: int
    price_distribution: Dict[str, int]
    review_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    missing_values: Dict[str, int]