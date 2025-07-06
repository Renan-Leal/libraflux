from nest.core import Module
from .auth_controller import AuthController


@Module(controllers=[AuthController])
class AuthModule:
    pass
