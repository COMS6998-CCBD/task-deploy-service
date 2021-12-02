from typing import List
from constants import *

class TaskDeployRequest:
    def __init__(self, user_id: str, task_id: str, task_name: str, s3_bucket: str, source_s3_prefix: str, destination_s3_prefix: str, command: str, linux_dependencies: List[str]):
        self.user_id = user_id
        self.task_id = task_id
        self.task_name = task_name
        self.s3_bucket = s3_bucket
        self.source_s3_prefix = source_s3_prefix
        self.destination_s3_prefix = destination_s3_prefix
        self.command = command
        self.linux_dependencies = linux_dependencies