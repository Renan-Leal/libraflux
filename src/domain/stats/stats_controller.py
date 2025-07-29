from nest.core import Controller, Get
from .stats_service import StatsService
from .dto.stats_dto import OverviewStatsResponse, CategoryStats
from typing import Dict
from ..auth.auth_guard import get_current_user
from fastapi import Depends


@Controller("/stats")
class StatsController:
    def __init__(self, service: StatsService):
        self.service = service

    @Get("/overview")
    def get_overview(self, user=Depends(get_current_user)):
        """
        Retorna uma visão geral das estatísticas dos livros.
        """
        return self.service.get_overview()

    @Get("/categories")
    def get_categories_stats(self, user=Depends(get_current_user)):
        """
        Retorna as estatísticas por categoria .
        """
        return self.service.get_categories_stats()
      