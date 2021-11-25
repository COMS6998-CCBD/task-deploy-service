from constants import *

class TaskDeployRequest:
    def __init__(self, userId, uniqueId, s3_bucket, source_s3_path, destination_s3_path, command, linux_dependencies):
        self.userId = userId
        self.uniqueId = uniqueId
        self.s3_bucket = s3_bucket
        self.source_s3_path = source_s3_path
        self.destination_s3_path = destination_s3_path
        self.command = command
        self.linux_dependencies = linux_dependencies