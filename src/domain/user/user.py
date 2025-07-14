from ...infra.models.user_model import UserModel
from ...common.enums import UserRole


class User:
    def __init__(
        self,
        email: str,
        name: str,
        password: str,
        role="REGULAR",
    ):
        self.email = email
        self.name = name
        self.password = password
        self.role = role

    def to_user_model(self):
        return UserModel(
            email=self.email,
            name=self.name,
            password=self.password,
            role=UserRole(self.role),
        )
