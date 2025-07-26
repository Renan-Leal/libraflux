from nest.core import Controller, Get
from .categories_service import CategoriesService
from .dto.categories_dto import CategoryListResponse
from typing import List
from ..auth.auth_guard import get_current_user
from fastapi import Depends


@Controller("/categories")
class CategoriesController:
    def __init__(self, categories_service: CategoriesService):
        self.categories_service = categories_service

    @Get("/")
    def get_all_categories(
        self, user=Depends(get_current_user)
    ) -> List[CategoryListResponse]:
        """
        Retorna todas as categorias disponíveis.
        """
        return self.categories_service.get_all_categories()
