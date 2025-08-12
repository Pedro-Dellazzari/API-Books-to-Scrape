from database.connection import get_connection
from models.ml_responses import BookFeature, MLFeatures, TrainingRecord, TrainingDataset
from typing import Dict, List, Any, Tuple
import psycopg2.extras
import statistics
from datetime import datetime
import re

class MLDataProcessor:
    """Classe para processamento de dados para Machine Learning"""
    
    def __init__(self):
        self.category_mapping = {}
        self.review_mapping = {
            'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5
        }
        self.price_categories = {
            'budget': (0, 20),
            'mid': (20, 50),
            'premium': (50, float('inf'))
        }
    
    def _get_raw_data(self) -> List[Dict[str, Any]]:
        """Busca dados brutos do banco de dados"""
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
            WHERE titulo IS NOT NULL 
            AND categoria IS NOT NULL 
            AND valor_principal_em_euros IS NOT NULL
            ORDER BY titulo
        """
        
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(sql)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def _create_category_mapping(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Cria mapeamento de categorias para valores numéricos"""
        categories = set(row['categoria'] for row in data if row['categoria'])
        return {cat: idx for idx, cat in enumerate(sorted(categories))}
    
    def _normalize_prices(self, prices: List[float]) -> Tuple[float, float]:
        """Calcula estatísticas para normalização de preços"""
        if not prices:
            return 0.0, 1.0
        mean_price = statistics.mean(prices)
        stdev_price = statistics.stdev(prices) if len(prices) > 1 else 1.0
        return mean_price, stdev_price
    
    def _extract_features(self, row: Dict[str, Any], 
                         category_mapping: Dict[str, int],
                         price_stats: Dict[str, Tuple[float, float]]) -> BookFeature:
        """Extrai features de um registro"""
        
        # Features básicas
        titulo = row['titulo'] or ''
        titulo_length = len(titulo)
        titulo_word_count = len(titulo.split())
        
        # Categoria encoded
        categoria_encoded = category_mapping.get(row['categoria'], 0)
        
        # Preços normalizados
        preco_euros = float(row['valor_principal_em_euros'] or 0)
        preco_reais = float(row['valor_principal_em_reais'] or 0)
        
        euros_mean, euros_std = price_stats['euros']
        reais_mean, reais_std = price_stats['reais']
        
        preco_euros_normalized = (preco_euros - euros_mean) / euros_std if euros_std > 0 else 0
        preco_reais_normalized = (preco_reais - reais_mean) / reais_std if reais_std > 0 else 0
        
        # Review score
        review_score = self.review_mapping.get(row['review'], 0)
        
        # Features derivadas
        has_discount = preco_euros < euros_mean * 0.8  # Desconto se preço < 80% da média
        
        # Categoria de preço
        if preco_euros <= 20:
            price_category = 'budget'
        elif preco_euros <= 50:
            price_category = 'mid'
        else:
            price_category = 'premium'
        
        return BookFeature(
            upc_livro=row['upc_livro'],
            titulo_length=titulo_length,
            categoria_encoded=categoria_encoded,
            preco_euros_normalized=round(preco_euros_normalized, 4),
            preco_reais_normalized=round(preco_reais_normalized, 4),
            review_score=review_score,
            titulo_word_count=titulo_word_count,
            categoria=row['categoria'],
            has_discount=has_discount,
            price_category=price_category
        )
    
    def get_features(self, limit: int = 1000) -> MLFeatures:
        """Gera dataset de features para ML"""
        
        # Busca dados brutos
        raw_data = self._get_raw_data()
        
        if limit:
            raw_data = raw_data[:limit]
        
        # Cria mapeamentos
        self.category_mapping = self._create_category_mapping(raw_data)
        
        # Calcula estatísticas de preços
        euros_prices = [float(row['valor_principal_em_euros'] or 0) for row in raw_data]
        reais_prices = [float(row['valor_principal_em_reais'] or 0) for row in raw_data]
        
        price_stats = {
            'euros': self._normalize_prices(euros_prices),
            'reais': self._normalize_prices(reais_prices)
        }
        
        # Extrai features
        features = []
        for row in raw_data:
            try:
                feature = self._extract_features(row, self.category_mapping, price_stats)
                features.append(feature)
            except Exception as e:
                print(f"Erro ao processar linha {row.get('upc_livro', 'N/A')}: {e}")
                continue
        
        # Metadados
        feature_columns = [
            'titulo_length', 'categoria_encoded', 'preco_euros_normalized',
            'preco_reais_normalized', 'review_score', 'titulo_word_count',
            'has_discount', 'price_category'
        ]
        
        normalization_stats = {
            'preco_euros': {
                'mean': price_stats['euros'][0],
                'std': price_stats['euros'][1]
            },
            'preco_reais': {
                'mean': price_stats['reais'][0],
                'std': price_stats['reais'][1]
            }
        }
        
        return MLFeatures(
            total_records=len(features),
            feature_columns=feature_columns,
            categorical_mappings={
                'categoria': self.category_mapping,
                'review': self.review_mapping,
                'price_category': {'budget': 0, 'mid': 1, 'premium': 2}
            },
            normalization_stats=normalization_stats,
            features=features,
            metadata={
                'generated_at': datetime.now().isoformat(),
                'data_source': 'livros_table',
                'preprocessing_applied': [
                    'category_encoding',
                    'price_normalization',
                    'text_feature_extraction',
                    'derived_features'
                ]
            }
        )
    
    def get_training_data(self, limit: int = 1000) -> TrainingDataset:
        """Gera dataset para treinamento com target variable"""
        
        # Busca dados brutos
        raw_data = self._get_raw_data()
        
        if limit:
            raw_data = raw_data[:limit]
        
        # Cria mapeamentos
        self.category_mapping = self._create_category_mapping(raw_data)
        
        # Calcula estatísticas
        euros_prices = [float(row['valor_principal_em_euros'] or 0) for row in raw_data]
        reais_prices = [float(row['valor_principal_em_reais'] or 0) for row in raw_data]
        
        price_stats = {
            'euros': self._normalize_prices(euros_prices),
            'reais': self._normalize_prices(reais_prices)
        }
        
        # Critério para "popular" - livros com review >= 4 e preço <= mediana
        median_price = statistics.median(euros_prices) if euros_prices else 0
        
        # Gera registros de treinamento
        training_records = []
        for row in raw_data:
            try:
                # Features básicas
                titulo = row['titulo'] or ''
                preco_euros = float(row['valor_principal_em_euros'] or 0)
                preco_reais = float(row['valor_principal_em_reais'] or 0)
                review_score = self.review_mapping.get(row['review'], 0)
                
                # Target variable - livro é popular se tem boa avaliação E preço acessível
                target_popular = review_score >= 4 and preco_euros <= median_price
                
                # Features processadas
                euros_mean, euros_std = price_stats['euros']
                reais_mean, reais_std = price_stats['reais']
                
                record = TrainingRecord(
                    upc_livro=row['upc_livro'],
                    titulo=titulo,
                    categoria=row['categoria'],
                    preco_euros=preco_euros,
                    preco_reais=preco_reais,
                    review=row['review'],
                    titulo_length=len(titulo),
                    titulo_word_count=len(titulo.split()),
                    categoria_encoded=self.category_mapping.get(row['categoria'], 0),
                    preco_euros_normalized=round((preco_euros - euros_mean) / euros_std if euros_std > 0 else 0, 4),
                    preco_reais_normalized=round((preco_reais - reais_mean) / reais_std if reais_std > 0 else 0, 4),
                    review_score=review_score,
                    has_discount=preco_euros < euros_mean * 0.8,
                    price_category='budget' if preco_euros <= 20 else ('mid' if preco_euros <= 50 else 'premium'),
                    target_popular=target_popular
                )
                
                training_records.append(record)
                
            except Exception as e:
                print(f"Erro ao processar linha {row.get('upc_livro', 'N/A')}: {e}")
                continue
        
        # Estatísticas do dataset
        total_popular = sum(1 for r in training_records if r.target_popular)
        
        statistics_data = {
            'total_records': len(training_records),
            'target_distribution': {
                'popular': total_popular,
                'not_popular': len(training_records) - total_popular,
                'popular_percentage': round(total_popular / len(training_records) * 100, 2) if training_records else 0
            },
            'price_stats': {
                'mean_euros': round(statistics.mean([r.preco_euros for r in training_records]), 2) if training_records else 0,
                'median_euros': round(statistics.median([r.preco_euros for r in training_records]), 2) if training_records else 0,
                'std_euros': round(statistics.stdev([r.preco_euros for r in training_records]), 2) if len(training_records) > 1 else 0
            },
            'review_distribution': {
                str(score): sum(1 for r in training_records if r.review_score == score) 
                for score in range(0, 6)
            }
        }
        
        return TrainingDataset(
            total_records=len(training_records),
            train_test_split_info={
                'recommended_train_size': 0.8,
                'recommended_test_size': 0.2,
                'stratify_by': 'target_popular'
            },
            feature_descriptions={
                'titulo_length': 'Número de caracteres no título',
                'titulo_word_count': 'Número de palavras no título',
                'categoria_encoded': 'Categoria codificada numericamente',
                'preco_euros_normalized': 'Preço em euros normalizado (z-score)',
                'preco_reais_normalized': 'Preço em reais normalizado (z-score)',
                'review_score': 'Score da avaliação (1-5)',
                'has_discount': 'Se o livro tem desconto (preço < 80% da média)',
                'price_category': 'Categoria de preço (budget/mid/premium)',
                'target_popular': 'Variável alvo - se o livro é popular (review >= 4 e preço <= mediana)'
            },
            target_variable='target_popular',
            data=training_records,
            statistics=statistics_data,
            created_at=datetime.now()
        )