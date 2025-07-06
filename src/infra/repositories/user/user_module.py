from nest.core import Module
from .user_repository import UserRepository


@Module(providers=[UserRepository], exports=[UserRepository])
class UserRepositoryModule:
    pass
