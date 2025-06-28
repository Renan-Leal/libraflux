from nest.core import Module
from .scraping_service import ScrapingService
from .scraping_controller import ScrapingController
from .book_scraper import BookScraper
from ...infra.repositories.book_repository_module import BookRepositoryModule


@Module(
    imports=[BookRepositoryModule],
    providers=[BookScraper, ScrapingService],
    controllers=[ScrapingController],
)
class ScrapingModule:
    pass
