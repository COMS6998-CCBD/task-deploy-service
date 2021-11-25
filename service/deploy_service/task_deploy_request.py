from constants import *

class TaskDeployRequest:
    def __init__(self):
        self.userId = ""
        self.uniqueId = ""
        self.s3_bucket = ""
        self.source_s3_path = ""
        self.destination_s3_path = ""
        self.command = ""
        self.linux_dependencies = []