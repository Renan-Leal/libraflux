import os
import hashlib
from nest.core import Injectable
from .dtos.auth_signup import AuthSignup
from ..user.user import User
from ...infra.repositories.user.user_repository import UserRepository

@Injectable
class AuthService:
    def __init__(self, userRepository: UserRepository):
        self.userRepository = userRepository

    def signup(self, authSignup: AuthSignup):
        secret = os.environ.get("JWT_SECRET_KEY", "")
        password_hash = hashlib.sha256((authSignup.password + secret).encode()).hexdigest()
        user = User(
            authSignup.email,
            authSignup.name,
            password_hash,
            authSignup.role if hasattr(authSignup, "role") else None
        )
        user_model = user.to_user_model()
        try:
            created_user = self.userRepository.save(user_model)
            if created_user:
                return {
                    "email": created_user.email,
                    "name": created_user.name,
                    "role": created_user.role.value if hasattr(created_user.role, "value") else str(created_user.role),
                    "message": "User created successfully"
                }, 201
            else:
                return {"message": "Failed to create user"}, 400
        except Exception as e:
            return {"message": f"Failed to create user: {str(e)}"}, 400