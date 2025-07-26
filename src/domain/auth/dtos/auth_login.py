from ....common.validators import BaseModel, ConstrainedStr, EmailStr, Optional


class AuthLogin(BaseModel):
    email: EmailStr
    password: ConstrainedStr
