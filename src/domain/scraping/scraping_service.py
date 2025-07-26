import time
from nest.core import Injectable
from .book_scraper import BookScraper
from .dtos.scraped_book import ScrapedBook
from ...infra.repositories.book.book_repository import BookRepository
from ...infra.logs.logging_service import LoggingService


@Injectable
class ScrapingService:
    def __init__(self, book_scraper: BookScraper, repository: BookRepository, logger: LoggingService = None):
        self.book_scraper = book_scraper
        self.repository = repository
        self.logger = logger or LoggingService("ScrapingService")

    async def trigger(self):
        """
        Executa o scraping dos livros e salva no banco de dados.
        """
        start_time = time.time()
        
        # Log início do processo
        self.logger.info(
            "Starting book scraping process",
            operation="scraping_start"
        )
        
        try:
            # Executar scraping
            scraping_start = time.time()
            book_list = self.book_scraper.execute()
            scraping_duration = (time.time() - scraping_start) * 1000
            
            # Log resultado do scraping
            self.logger.log_business_operation(
                "book_scraping",
                "completed",
                scraping_duration,
                scraping_stats={
                    "books_scraped": len(book_list),
                    "source": "external_api"
                }
            )
            
            # Processar dados coletados
            processing_start = time.time()
            book_model_list = []
            processed_books = 0
            failed_books = 0
            
            for book_data in book_list:
                try:
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
                    processed_books += 1
                    
                except Exception as e:
                    failed_books += 1
                    self.logger.warning(
                        f"Failed to process book data: {str(e)}",
                        operation="book_processing_error",
                        error_data={
                            "error_message": str(e),
                            "book_data": book_data,
                            "error_type": type(e).__name__
                        }
                    )
            
            processing_duration = (time.time() - processing_start) * 1000
            
            # Log processamento dos dados
            self.logger.log_business_operation(
                "book_data_processing",
                "completed", 
                processing_duration,
                processing_stats={
                    "processed_books": processed_books,
                    "failed_books": failed_books,
                    "success_rate": (processed_books / len(book_list)) * 100 if book_list else 0
                }
            )
            
            # Salvar no banco de dados
            if book_model_list:
                db_start = time.time()
                self.repository.create_many(book_model_list)
                db_duration = (time.time() - db_start) * 1000
                
                # Log operação de banco
                self.logger.log_business_operation(
                    "book_database_save",
                    "completed",
                    db_duration,
                    database_stats={
                        "books_saved": len(book_model_list),
                        "operation_type": "bulk_insert"
                    }
                )
            else:
                self.logger.warning(
                    "No books to save to database",
                    operation="database_save_skipped",
                    reason="no_valid_books_processed"
                )
            
            # Log conclusão do processo completo
            total_duration = (time.time() - start_time) * 1000
            self.logger.info(
                f"Scraping process completed successfully",
                operation="scraping_complete",
                final_stats={
                    "total_duration_ms": total_duration,
                    "books_scraped": len(book_list),
                    "books_processed": processed_books,
                    "books_saved": len(book_model_list),
                    "failed_processing": failed_books,
                    "overall_success": True
                }
            )
            
            return {
                "status": "success",
                "books_scraped": len(book_list),
                "books_saved": len(book_model_list),
                "duration_ms": total_duration
            }
            
        except Exception as e:
            total_duration = (time.time() - start_time) * 1000
            
            # Log erro crítico
            self.logger.error(
                f"Scraping process failed: {str(e)}",
                operation="scraping_failed",
                error_data={
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": total_duration
                },
                final_stats={
                    "overall_success": False,
                    "total_duration_ms": total_duration
                }
            )
            
            raise Exception(f"Scraping process failed: {str(e)}")
