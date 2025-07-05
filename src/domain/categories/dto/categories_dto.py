from pydantic import BaseModel


class CategoryListResponse(BaseModel):
    category: str
