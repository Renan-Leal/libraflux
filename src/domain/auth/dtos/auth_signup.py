from ....common.validators import BaseModel, ConstrainedStr, EmailStr, Optional
from ....common.enums import UserRole


class AuthSignup(BaseModel):
    email: EmailStr
    name: ConstrainedStr
    password: ConstrainedStr
    role: Optional[UserRole] = UserRole.REGULAR
