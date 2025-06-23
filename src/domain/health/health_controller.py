from nest.core import Controller, Get
from .health_service import HealthService


@Controller("/health")
class HealthController:

    def __init__(self, service: HealthService):
        self.service = service

    @Get("/check")
    def check(self):
        return self.service.check()
