from nest.core import Module
from .ml_controller import MlController
from .ml_service import MlService
from ...infra.repositories.book_repository_module import BookRepositoryModule


@Module(
    imports=[BookRepositoryModule],
    providers=[MlService],
    controllers=[MlController],
)
class MlModule:
    pass
