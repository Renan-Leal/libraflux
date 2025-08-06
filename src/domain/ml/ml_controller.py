from nest.core import Controller, Get, Post
from .ml_service import MlService
from .dto.ml_dto import (
    BookFeatureResponse,
    TrainingDataResponse,
    PredictionRequest,
    PredictionResponse,
)
from typing import List
from ..auth.auth_guard import get_current_user
from fastapi import Depends


@Controller("/ml")
class MlController:
    def __init__(self, service: MlService):
        self.service = service

    @Get("/features", description="Dados formatados para features.")
    def get_features(self, user=Depends(get_current_user)) -> List[BookFeatureResponse]:
        """Dados formatados para features.

        Returns:
            book_id: str
            category: str
            rating: int
            price: float
            availability: int
            description_length: int
        """
        return self.service.get_features()

    @Get("/training-data", description="Dataset para treinamento.")
    def get_training_data(self, user=Depends(get_current_user)) -> List[TrainingDataResponse]:
        """Dataset para treinamento.

        Returns:
            # features
            category: str
            price: float
            availability: int
            description_length: int
            # target
            rating: int
        """
        return self.service.get_training_data()

    @Post("/predictions", description="Endpoint para receber predições.")
    def post_predictions(self, prediction: PredictionRequest, user=Depends(get_current_user)) -> PredictionResponse:
        """Endpoint para receber predições.

        Args:
            book_id: str
            predicted_rating: float

        Returns:
            message: str
            prediction_id: Optional[int] = None
        """
        return self.service.save_prediction(prediction)
