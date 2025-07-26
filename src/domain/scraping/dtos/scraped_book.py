from ....infra.models.book_model import BookModel


class ScrapedBook:
    def __init__(
        self,
        uuid: str,
        title: str,
        category: str,
        rating: int,
        price_excl_tax: float,
        price_incl_tax: float,
        tax: float,
        availability: int = 0,
        reviews_qtd: int = 0,
        description: str = None,
        image: str = None,
    ):
        self.uuid = uuid
        self.title = title
        self.category = category
        self.rating = rating
        self.price_excl_tax = price_excl_tax
        self.price_incl_tax = price_incl_tax
        self.tax = tax
        self.availability = availability
        self.reviews_qtd = reviews_qtd
        self.description = description
        self.image = image

    def to_book_model(self):
        return BookModel(
            uuid=self.uuid,
            title=self.title,
            category=self.category,
            rating=self.rating,
            price_excl_tax=self.price_excl_tax,
            price_incl_tax=self.price_incl_tax,
            tax=self.tax,
            availability=self.availability,
            reviews_qtd=self.reviews_qtd,
            description=self.description,
            image=self.image,
        )
