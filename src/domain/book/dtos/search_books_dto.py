from ....common.validators import BaseModel, ConstrainedStr


class SearchBookDTO(BaseModel):
    title: ConstrainedStr
    category: ConstrainedStr
