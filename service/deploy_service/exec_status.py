from enum import Enum

class EXEC_STATUS(Enum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    EXECUTED = "EXECUTED"
    COPIED = "COPIED"
    DELETED = "DELETED"