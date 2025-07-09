from nest.core import Controller, Get
from .stats_service import StatsService

@Controller("/stats")
class StatsController:
    def __init__(self, service: StatsService):
        self.service = service

    @Get("/overview")
    def get_overview(self):
        return self.service.get_overview()

    @Get("/categories")
    def get_categories_stats(self):
        return self.service.get_categories_stats()