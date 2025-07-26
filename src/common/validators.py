from typing import Annotated
from pydantic import BaseModel, StringConstraints, EmailStr
from typing import Optional


"""Validação de dados comuns para o sistema de autenticação."""
ConstrainedStr = Annotated[str, StringConstraints(min_length=6)]
# add validators
