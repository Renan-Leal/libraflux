from collections import defaultdict
from nest.core import Injectable
from ...infra.repositories.book.book_repository import BookRepository


@Injectable
class StatsService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def get_overview(self):
        """Calcula as estatisticas gerais.
        (total de livros, preço médio, distribuição de ratings)

        Returns:
        dict: "total_books": int, "average_price": float, "rating_distribution": dict{str: int}
        """
        books = self.repository.list_all()
        total_books = len(books)

        if total_books == 0:
            return {
                "total_books": 0,
                "average_price": 0,
                "rating_distribution": {},
            }

        total_price = sum(
            float(book.price_incl_tax) for book in books if book.price_incl_tax
        )
        average_price = total_price / total_books if total_books > 0 else 0

        rating_distribution = defaultdict(int)
        for book in books:
            if hasattr(book, "rating") and book.rating and 0 < book.rating <= 5:
                rating_distribution[book.rating] += 1

        return {
            "total_books": total_books,
            "average_price": round(average_price, 2),
            "rating_distribution": dict(sorted(rating_distribution.items())),
        }

    def get_categories_stats(self):
        """
        Calcula as estatisticas por categoria.
        (numero de livros, preço por categoria).

        Returns:
        dict: "book_count": int, "average_price": float
        """
        books = self.repository.list_all()

        category_stats = defaultdict(lambda: {"book_count": 0, "total_price": 0.0})

        for book in books:
            category = book.category
            category_stats[category]["book_count"] += 1
            if book.price_incl_tax:
                category_stats[category]["total_price"] += float(book.price_incl_tax)

        category_stats_results = {}
        for category, data in category_stats.items():
            book_count = data["book_count"]
            average_price = data["total_price"] / book_count if book_count > 0 else 0
            category_stats_results[category] = {
                "book_count": book_count,
                "average_price": round(average_price, 2),
            }

        return category_stats_results
