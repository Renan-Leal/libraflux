from nest.core import Injectable
from .book_scraper import BookScraper


@Injectable
class ScrapingService:
    def __init__(self, book_scraper: BookScraper):
        self.book_scraper = book_scraper

    async def trigger(self):
        return self.book_scraper.execute()
