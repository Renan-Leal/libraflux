from typing import Annotated
from pydantic import BaseModel, StringConstraints, EmailStr
from typing import Optional

ConstrainedStr = Annotated[str, StringConstraints(min_length=6)]
# add validators
