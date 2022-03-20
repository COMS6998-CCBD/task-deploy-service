from typing import List
from constants import *

class TaskDeployRequest:
    def __init__(self, 
            user_id: str,
            task_id: str,
            task_name: str,
            exec_id: str, 
            s3_bucket: str, 
            source_s3_prefix: str, 
            command: str, 
            cron_expression: str=None,
            linux_dependencies: List[str] = []
            ):
        self.user_id = user_id
        self.exec_id = exec_id
        self.task_id = task_id
        self.task_name = task_name
        self.s3_bucket = s3_bucket
        self.source_s3_prefix = source_s3_prefix
        self.command = command
        self.linux_dependencies = linux_dependencies
        self.cron_expression = cron_expression
        if type(self.linux_dependencies) == type(""):
            self.linux_dependencies = self.linux_dependencies.split(",")
            self.linux_dependencies = [dep.strip() for dep in self.linux_dependencies]