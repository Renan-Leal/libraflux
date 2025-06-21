from nest.core import Module
from .scraping_service import ScrapingService
from .scraping_controller import ScrapingController
from .book_scraper import BookScraper


@Module(providers=[BookScraper, ScrapingService], controllers=[ScrapingController])
class ScrapingModule:
    pass
