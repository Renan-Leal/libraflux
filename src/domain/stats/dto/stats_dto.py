from ....common.validators import BaseModel
from typing import Dict


class OverviewStatsResponse(BaseModel):
    """Estatísticas gerais (total de livros, preço médio, distribuição de ratings).

    Returns:
        total_books: int
        average_price: float
        rating_distribution: Dict[int, int]
    """
    total_books: int
    average_price: float
    rating_distribution: Dict[int, int]


class CategoryStats(BaseModel):
    """Estatísticas detalhadas por categoria (quantidade de livros, preços por categoria).

    Returns:
        book_count: int
        average_price: float
    """
    book_count: int
    average_price: float
