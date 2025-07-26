from nest.core import Module
from .categories_controller import CategoriesController
from .categories_service import CategoriesService


@Module(controllers=[CategoriesController], providers=[CategoriesService])
class CategoriesModule:
    pass
