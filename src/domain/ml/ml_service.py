from nest.core import Injectable
from ...infra.repositories.book.book_repository import BookRepository
from ...infra.logs.logging_service import LoggingService
from .dto.ml_dto import (
    BookFeatureResponse,
    TrainingDataResponse,
    PredictionRequest,
    PredictionResponse,
)
from typing import List


@Injectable
class MlService:
    def __init__(self, repository: BookRepository, logger: LoggingService):
        self.repository = repository
        self.logger = logger

    def get_features(self) -> List[BookFeatureResponse]:
        """
        Formata os dados dos livros como features para modelos de ML.
        """
        books = self.repository.list_all()
        features = []
        for book in books:
            features.append(
                BookFeatureResponse(
                    book_id=book.uuid,
                    category=book.category,
                    rating=book.rating,
                    price=float(book.price_incl_tax) if book.price_incl_tax else 0.0,
                    availability=book.availability,
                    description_length=len(book.description) if book.description else 0,
                )
            )
        return features

    def get_training_data(self) -> List[TrainingDataResponse]:
        """
        Cria um dataset para treinamento de modelos de ML, separando features e target.
        """
        books = self.repository.list_all()
        return [
            TrainingDataResponse(
                category=book.category,
                price=float(book.price_incl_tax) if book.price_incl_tax else 0.0,
                availability=book.availability,
                description_length=len(book.description) if book.description else 0,
                rating=book.rating,
            )
            for book in books
        ]

    def save_prediction(self, prediction_data: PredictionRequest) -> PredictionResponse:
        """
        Recebe e loga uma predição de um modelo de ML.
        """
        self.logger.info(
            f"Received prediction for book {prediction_data.book_id}: "
            f"Predicted Rating = {prediction_data.predicted_rating}"
        )
        return PredictionResponse(message="Prediction received successfully.")
