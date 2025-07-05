from nest.core import Controller, Get
from .categories_service import CategoriesService
from .dto.categories_dto import CategoryListResponse
from typing import List


@Controller("/categories")
class CategoriesController:
    def __init__(self, categories_service: CategoriesService):
        self.categories_service = categories_service

    @Get("/")
    def get_all_categories(self) -> List[CategoryListResponse]:
        return self.categories_service.get_all_categories()
