from nest.core import Controller, Get
from .stats_service import StatsService
from .dto.stats_dto import OverviewStatsResponse, CategoryStats
from typing import Dict


@Controller("/stats")
class StatsController:
    def __init__(self, service: StatsService):
        self.service = service

    @Get("/overview")
    def get_overview(self) -> OverviewStatsResponse:
        return self.service.get_overview()

    @Get("/categories")
    def get_categories_stats(self) -> Dict[str, CategoryStats]:
        return self.service.get_categories_stats()
