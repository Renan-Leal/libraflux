import time
from nest.core import Injectable
from ...infra.repositories.book.book_repository import BookRepository
from ...infra.logs.logging_service import LoggingService


@Injectable
class BookService:
    def __init__(self, repository: BookRepository, logger: LoggingService = None):
        self.repository = repository
        self.logger = logger or LoggingService("BookService")

    def list_books(self):
        """List all books in the database."""
        start_time = time.time()
        
        self.logger.info(
            "Starting to list all books",
            operation="list_all_books_start"
        )
        
        try:
            books = self.repository.list_all()
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_business_operation(
                "list_all_books",
                "completed",
                duration_ms,
                query_stats={
                    "books_found": len(books),
                    "query_type": "list_all"
                }
            )
            
            return books
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"Failed to list books: {str(e)}",
                operation="list_books_error",
                error_data={
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": duration_ms
                }
            )
            raise

    def list_books_paginated(self, page: int, size: int):
        """
        Retorna uma lista paginada de livros.
        """
        start_time = time.time()
        
        self.logger.info(
            f"Starting paginated book query: page {page}, size {size}",
            operation="list_books_paginated_start",
            query_params={
                "page": page,
                "size": size
            }
        )
        
        try:
            start = (page - 1) * size
            end = start + size
            books = self.list_books()  # Método que retorna todos os livros
            paginated_books = books[start:end]
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_business_operation(
                "list_books_paginated",
                "completed",
                duration_ms,
                query_stats={
                    "page": page,
                    "size": size,
                    "total_books": len(books),
                    "returned_books": len(paginated_books),
                    "start_index": start,
                    "end_index": end
                }
            )
            
            return paginated_books
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"Failed to get paginated books: {str(e)}",
                operation="list_books_paginated_error",
                error_data={
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": duration_ms,
                    "page": page,
                    "size": size
                }
            )
            raise

    def get_book_by_id(self, id: int):
        """
        Retorna um livro pelo ID.
        Exemplo: /books/1
        """
        start_time = time.time()
        
        self.logger.info(
            f"Starting book lookup by ID: {id}",
            operation="get_book_by_id_start",
            query_params={
                "book_id": id
            }
        )
        
        try:
            book = self.repository.get_by_id(id)
            duration_ms = (time.time() - start_time) * 1000
            
            if book:
                self.logger.log_business_operation(
                    "get_book_by_id",
                    "found",
                    duration_ms,
                    query_stats={
                        "book_id": id,
                        "book_title": book.title if hasattr(book, 'title') else "unknown",
                        "found": True
                    }
                )
            else:
                self.logger.log_business_operation(
                    "get_book_by_id",
                    "not_found",
                    duration_ms,
                    query_stats={
                        "book_id": id,
                        "found": False
                    }
                )
            
            return book
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"Failed to get book by ID {id}: {str(e)}",
                operation="get_book_by_id_error",
                error_data={
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": duration_ms,
                    "book_id": id
                }
            )
            raise

    def search_books(self, title: str = None, category: str = None):
        """
        Busca livros por título e/ou categoria.
        Exemplo: /books/search?title={Title}&category={Category}
        """
        start_time = time.time()
        
        self.logger.info(
            f"Starting book search: title={title}, category={category}",
            operation="search_books_start",
            query_params={
                "title": title,
                "category": category,
                "search_type": self._get_search_type(title, category)
            }
        )
        
        try:
            books = []
            
            if (title and title.strip()) and (category and category.strip()):
                books = self.repository.list_bycategoryandtitle(title, category)
                search_type = "title_and_category"
            elif title and title.strip():
                books = self.repository.list_bytitle(title)
                search_type = "title_only"
            elif category and category.strip():
                books = self.repository.list_bycategory(category)
                search_type = "category_only"
            else:
                books = []
                search_type = "empty_query"
            
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_business_operation(
                "search_books",
                "completed",
                duration_ms,
                query_stats={
                    "title": title,
                    "category": category,
                    "search_type": search_type,
                    "results_found": len(books)
                }
            )
            
            return books
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"Failed to search books: {str(e)}",
                operation="search_books_error",
                error_data={
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": duration_ms,
                    "title": title,
                    "category": category
                }
            )
            raise

    def get_top_rated_books(self):
        """
        Retorna uma lista de livros bem avaliados (exemplo: rating >= 4).
        """
        start_time = time.time()
        
        self.logger.info(
            "Starting top rated books query",
            operation="get_top_rated_books_start"
        )
        
        try:
            books = self.repository.get_top_rated_books()
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_business_operation(
                "get_top_rated_books",
                "completed",
                duration_ms,
                query_stats={
                    "top_rated_books_found": len(books),
                    "query_type": "top_rated"
                }
            )
            
            return books
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"Failed to get top rated books: {str(e)}",
                operation="get_top_rated_books_error",
                error_data={
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": duration_ms
                }
            )
            raise

    def list_books_by_price_range(self, min_price: float, max_price: float):
        """
        Lista livros dentro de um intervalo de preços.
        Exemplo: /books/price-range?min_price=10.0&max_price=50.0
        """
        start_time = time.time()
        
        self.logger.info(
            f"Starting price range query: {min_price} - {max_price}",
            operation="list_books_by_price_range_start",
            query_params={
                "min_price": min_price,
                "max_price": max_price,
                "price_range": max_price - min_price
            }
        )
        
        try:
            books = self.repository.list_by_price_range(min_price, max_price)
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.log_business_operation(
                "list_books_by_price_range",
                "completed",
                duration_ms,
                query_stats={
                    "min_price": min_price,
                    "max_price": max_price,
                    "books_found": len(books),
                    "query_type": "price_range"
                }
            )
            
            return books
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"Failed to get books by price range: {str(e)}",
                operation="list_books_by_price_range_error",
                error_data={
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": duration_ms,
                    "min_price": min_price,
                    "max_price": max_price
                }
            )
            raise

    def _get_search_type(self, title: str, category: str) -> str:
        """Helper para determinar o tipo de busca"""
        if title and category:
            return "title_and_category"
        elif title:
            return "title_only"
        elif category:
            return "category_only"
        else:
            return "empty_query"
