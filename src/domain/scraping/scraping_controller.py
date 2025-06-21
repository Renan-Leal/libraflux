from nest.core import Controller, Post
from .scraping_service import ScrapingService
from ...infra.logs.logging_service import LoggingService
from fastapi import BackgroundTasks


@Controller("/scraping")
class ScrapingController:

    def __init__(self, service: ScrapingService, logger: LoggingService):
        self.service = service
        self.logger = logger

    @Post("/trigger")
    def trigger(self, background_tasks: BackgroundTasks):
        background_tasks.add_task(self.service.trigger)
        return {
            "status": "INITIALIZED",
            "message": "Um e-mail será encaminhado ao final do processamento.",
        }
