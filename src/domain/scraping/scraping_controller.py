from nest.core import Controller, Post
from .scraping_service import ScrapingService
from ...infra.logs.logging_service import LoggingService
from fastapi import BackgroundTasks
from ...domain.auth.auth_guard import require_role
from fastapi import Depends


@Controller("/scraping")
class ScrapingController:

    def __init__(self, service: ScrapingService, logger: LoggingService):
        self.service = service
        self.logger = logger

    @Post("/trigger")
    def trigger(self, background_tasks: BackgroundTasks, user=Depends(require_role("ROOT"))):
        """
        Endpoint para iniciar o processo de scraping.
        Apenas usuários com a role ROOT podem acessar este endpoint.
        """
        background_tasks.add_task(self.service.trigger)
        return {
            "status": "INITIALIZED",
            "message": "Um e-mail será encaminhado ao final do processamento.",
        }
