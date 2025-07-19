from nest.core import Controller, Get, Post
from .ml_service import MlService
from .dto.ml_dto import (
    BookFeatureResponse,
    TrainingDataResponse,
    PredictionRequest,
    PredictionResponse,
)
from typing import List


@Controller("/ml")
class MlController:
    def __init__(self, service: MlService):
        self.service = service

    @Get("/features", description="Dados formatados para features.")
    def get_features(self) -> List[BookFeatureResponse]:
        return self.service.get_features()

    @Get("/training-data", description="Dataset para treinamento.")
    def get_training_data(self) -> List[TrainingDataResponse]:
        return self.service.get_training_data()

    @Post("/predictions", description="Endpoint para receber predições.")
    def post_predictions(self, prediction: PredictionRequest) -> PredictionResponse:
        return self.service.save_prediction(prediction)
