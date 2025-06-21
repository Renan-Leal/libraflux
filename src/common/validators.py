from typing import Annotated
from pydantic import BaseModel, StringConstraints

ConstrainedStr = Annotated[str, StringConstraints(min_length=6)]
# add validators
