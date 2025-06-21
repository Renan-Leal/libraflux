from nest.core import Module
from .logging_service import LoggingService


@Module(providers=[LoggingService], is_global=True)
class LoggingModule:
    pass
