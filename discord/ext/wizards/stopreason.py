from enum import Enum


class StopReason(Enum):
    CANCELLED = "cancelled"
    TIMED_OUT = "timed out"
    ERROR = "error"
