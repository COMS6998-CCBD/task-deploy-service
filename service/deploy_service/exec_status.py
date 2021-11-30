from enum import Enum

class EXEC_STATUS(Enum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    EXITED = "EXITED"
    COPIED = "COPIED"
    DELETED = "DELETED"