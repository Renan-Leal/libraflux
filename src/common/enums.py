from enum import Enum


class UserRole(Enum):
    """
    Enumeração para os papéis de usuário no sistema.
    Esta enumeração define os diferentes papéis que um usuário pode ter no sistema.
    """

    REGULAR = "REGULAR"
    ROOT = "ROOT"
