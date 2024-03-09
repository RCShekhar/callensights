from enum import Enum


class JobWorkflows(Enum):
    VENDOR: str = "VENDOR"
    PRIME_VENDOR: str = "PRIME_VENDOR"
    DIRECT_CLIENT: str = "DIRECT_CLIENT"
