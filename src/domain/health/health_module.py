from nest.core import Module
from .health_service import HealthService
from .health_controller import HealthController


@Module(imports=[], providers=[HealthService], controllers=[HealthController])
class HealthModule:
    pass
