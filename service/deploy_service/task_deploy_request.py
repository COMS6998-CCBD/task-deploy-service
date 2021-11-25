from constants import *

class TaskDeployRequest:
    def __init__(self, userId, uniqueId, s3_bucket, source_s3_prefix, destination_s3_prefix, command, linux_dependencies):
        self.userId = userId
        self.uniqueId = uniqueId
        self.s3_bucket = s3_bucket
        self.source_s3_prefix = source_s3_prefix
        self.destination_s3_prefix = destination_s3_prefix
        self.command = command
        self.linux_dependencies = linux_dependencies