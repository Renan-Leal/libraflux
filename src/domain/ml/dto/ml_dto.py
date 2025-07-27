from ....common.validators import BaseModel
from typing import Optional


class BookFeatureResponse(BaseModel):
    book_id: str
    category: str
    rating: int
    price: float
    availability: int
    description_length: int


class TrainingDataResponse(BaseModel):
    # features
    category: str
    price: float
    availability: int
    description_length: int
    # target
    rating: int


class PredictionRequest(BaseModel):
    book_id: str
    predicted_rating: float


class PredictionResponse(BaseModel):
    message: str
    prediction_id: Optional[int] = None
