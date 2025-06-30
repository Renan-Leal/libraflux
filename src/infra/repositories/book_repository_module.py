from nest.core import Module
from .book_repository import BookRepository


@Module(providers=[BookRepository], exports=[BookRepository])
class BookRepositoryModule:
    pass
