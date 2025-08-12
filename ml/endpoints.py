from fastapi import APIRouter, Depends, Query, HTTPException
from models.ml_responses import MLFeatures, TrainingDataset, MLStats
from models.auth import User
from auth.endpoints import get_current_active_user
from ml.data_processor import MLDataProcessor
from database.connection import get_connection
import psycopg2.extras
from typing import Optional

# Router para endpoints de Machine Learning
router = APIRouter(prefix="/api/v1/ml", tags=["Machine Learning"])

# Instância do processador de dados
ml_processor = MLDataProcessor()

@router.get("/features", response_model=MLFeatures)
async def get_ml_features(
    limit: Optional[int] = Query(1000, ge=10, le=5000, description="Limite de registros para processar"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna dados formatados para features de Machine Learning.
    
    Este endpoint processa os dados brutos dos livros e retorna:
    - Features numéricas normalizadas
    - Codificação de variáveis categóricas
    - Features derivadas (contagem de palavras, categorias de preço, etc.)
    - Metadados sobre o processamento
    
    Ideal para:
    - Análise exploratória de dados
    - Preparação de features para modelos
    - Validação de processamento de dados
    """
    try:
        features_data = ml_processor.get_features(limit=limit)
        
        if not features_data.features:
            raise HTTPException(
                status_code=404, 
                detail="Nenhum dado válido encontrado para processamento"
            )
            
        return features_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar features: {str(e)}"
        )

@router.get("/training-data", response_model=TrainingDataset)
async def get_training_data(
    limit: Optional[int] = Query(1000, ge=10, le=5000, description="Limite de registros para o dataset"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna dataset completo para treinamento de modelos de Machine Learning.
    
    Este endpoint fornece:
    - Dados preprocessados com features e target variable
    - Variável alvo: 'target_popular' (livro é popular baseado em review >= 4 e preço acessível)
    - Estatísticas do dataset
    - Informações para divisão treino/teste
    - Descrições detalhadas de cada feature
    
    Ideal para:
    - Treinamento de modelos de classificação
    - Análise de popularidade de livros
    - Estudos de correlação preço/qualidade
    """
    try:
        training_data = ml_processor.get_training_data(limit=limit)
        
        if not training_data.data:
            raise HTTPException(
                status_code=404,
                detail="Nenhum dado válido encontrado para treinamento"
            )
            
        return training_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar dataset de treinamento: {str(e)}"
        )

@router.get("/stats", response_model=MLStats)
async def get_ml_stats(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna estatísticas gerais dos dados para contexto de Machine Learning.
    
    Fornece insights sobre:
    - Distribuições de preços, categorias e reviews
    - Valores ausentes por coluna
    - Contagens gerais do dataset
    
    Útil para:
    - Análise exploratória inicial
    - Identificação de desbalanceamentos
    - Planejamento de estratégias de preprocessing
    """
    try:
        sql = """
            SELECT
                COUNT(*) as total_books,
                COUNT(DISTINCT categoria) as total_categories,
                COUNT(CASE WHEN valor_principal_em_euros <= 20 THEN 1 END) as budget_books,
                COUNT(CASE WHEN valor_principal_em_euros > 20 AND valor_principal_em_euros <= 50 THEN 1 END) as mid_books,
                COUNT(CASE WHEN valor_principal_em_euros > 50 THEN 1 END) as premium_books,
                COUNT(CASE WHEN review = 'One' THEN 1 END) as review_1,
                COUNT(CASE WHEN review = 'Two' THEN 1 END) as review_2,
                COUNT(CASE WHEN review = 'Three' THEN 1 END) as review_3,
                COUNT(CASE WHEN review = 'Four' THEN 1 END) as review_4,
                COUNT(CASE WHEN review = 'Five' THEN 1 END) as review_5,
                COUNT(CASE WHEN titulo IS NULL OR titulo = '' THEN 1 END) as missing_titles,
                COUNT(CASE WHEN categoria IS NULL OR categoria = '' THEN 1 END) as missing_categories,
                COUNT(CASE WHEN valor_principal_em_euros IS NULL THEN 1 END) as missing_prices,
                COUNT(CASE WHEN review IS NULL OR review = '' THEN 1 END) as missing_reviews
            FROM livros
        """
        
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(sql)
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Não foi possível obter estatísticas")
            
            # Busca distribuição de categorias
            cursor.execute("""
                SELECT categoria, COUNT(*) as count 
                FROM livros 
                WHERE categoria IS NOT NULL AND categoria != ''
                GROUP BY categoria 
                ORDER BY count DESC 
                LIMIT 10
            """)
            top_categories = dict(cursor.fetchall())
            
            return MLStats(
                total_books=result['total_books'],
                total_categories=result['total_categories'],
                price_distribution={
                    'budget': result['budget_books'],
                    'mid': result['mid_books'],
                    'premium': result['premium_books']
                },
                review_distribution={
                    '1': result['review_1'],
                    '2': result['review_2'],
                    '3': result['review_3'],
                    '4': result['review_4'],
                    '5': result['review_5']
                },
                category_distribution=top_categories,
                missing_values={
                    'titles': result['missing_titles'],
                    'categories': result['missing_categories'],
                    'prices': result['missing_prices'],
                    'reviews': result['missing_reviews']
                }
            )
            
        finally:
            conn.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )

@router.get("/health")
async def ml_health_check(current_user: User = Depends(get_current_active_user)):
    """Health check específico para módulo de ML"""
    try:
        # Testa processamento básico
        test_features = ml_processor.get_features(limit=10)
        
        return {
            "status": "healthy",
            "module": "machine_learning",
            "test_records_processed": len(test_features.features),
            "available_endpoints": ["/features", "/training-data", "/stats"],
            "data_processor": "operational"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "module": "machine_learning", 
            "error": str(e)
        }