from nest.core import Module
from .book_service import BookService
from .book_controller import BookController


@Module(imports=[], providers=[BookService], controllers=[BookController])
class BookModule:
    pass
