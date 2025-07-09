from nest.core import Module
from .stats_service import StatsService
from .stats_controller import StatsController
from ...infra.repositories.book_repository_module import BookRepositoryModule

@Module(
    imports=[BookRepositoryModule],
    providers=[StatsService],
    controllers=[StatsController],
)
class StatsModule:
    pass
