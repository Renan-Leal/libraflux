from pydantic import BaseModel
from typing import Dict


class OverviewStatsResponse(BaseModel):
    total_books: int
    average_price: float
    rating_distribution: Dict[int, int]


class CategoryStats(BaseModel):
    book_count: int
    average_price: float
