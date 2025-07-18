from nest.core import Injectable
from ...infra.db import SessionLocal
from ...infra.models import BookModel
from .dto.categories_dto import CategoryListResponse
from typing import List


@Injectable()
class CategoriesService:
    def __init__(self):
        self.session = SessionLocal

    def get_all_categories(self) -> List[CategoryListResponse]:
        """
        Retorna todas as categorias disponíveis.        
        """
        rows = self.session.query(BookModel.category).distinct().all()
        return [CategoryListResponse(category=row.category) for row in rows]
