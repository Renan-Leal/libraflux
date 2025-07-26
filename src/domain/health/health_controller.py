from nest.core import Controller, Get
from .health_service import HealthService
from ..auth.auth_guard import get_current_user
from fastapi import Depends


@Controller("/health")
class HealthController:

    def __init__(self, service: HealthService):
        self.service = service

    @Get("/check")
    def check(self, user=Depends(get_current_user)):
        """
        Endpoint para verificar a saúde do sistema.
        """
        return self.service.check()
