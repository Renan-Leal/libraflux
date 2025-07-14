from nest.core import Injectable
from .book_scraper import BookScraper
from .dtos.scraped_book import ScrapedBook
from ...infra.repositories.book.book_repository import BookRepository


@Injectable
class ScrapingService:
    def __init__(self, book_scraper: BookScraper, repository: BookRepository):
        self.book_scraper = book_scraper
        self.repository = repository

    async def trigger(self):
        book_list = self.book_scraper.execute()
        book_model_list = []
        for book_data in book_list:
            scraped_book = ScrapedBook(
                uuid=book_data.get("id"),
                title=book_data.get("title"),
                category=book_data.get("category"),
                rating=book_data.get("rating"),
                price_excl_tax=book_data.get("price_excl_tax"),
                price_incl_tax=book_data.get("price_incl_tax"),
                tax=book_data.get("tax"),
                availability=book_data.get("availability"),
                reviews_qtd=book_data.get("reviews_qtd", 0),
                description=book_data.get("description"),
                image=book_data.get("image"),
            )
            book_model = scraped_book.to_book_model()
            book_model_list.append(book_model)

        self.repository.create_many(book_model_list)
