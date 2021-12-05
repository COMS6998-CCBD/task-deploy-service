import boto3
from pathlib import Path
import logging

LOG = logging.getLogger("TDS")

class S3Manager:
    def __init__(self):
        self.client = boto3.client("s3")

    # TODO: execution_id hack fix
    def s3_to_local(self, s3_bucket: str, s3_path_prefix: str, local_dir: Path):
        s3_objects = self.client.list_objects_v2(Bucket=s3_bucket, Prefix=s3_path_prefix)
        LOG.info(f"s3 objects gotten are: {s3_objects}")
        for s3_object in s3_objects["Contents"]:
            object_name =s3_object["Key"]
            local_file_name = local_dir.joinpath(object_name)
            local_file_name = Path(str(local_file_name).replace(s3_path_prefix, ""))
            local_file_dir = local_file_name.parent
            LOG.info(f"Copying from {s3_bucket}:{object_name} to {local_file_name}")
            local_file_dir.mkdir(parents=True, exist_ok=True)
            self.client.download_file(Bucket=s3_bucket, Key=object_name, Filename=str(local_file_name))


    def local_to_s3(self, s3_bucket: str, s3_path_prefix: str, local_dir: Path):
        local_dir_str = str(local_dir)
        all_files = sorted(list(local_dir.rglob("**/*")))
        LOG.info(f"Uploading files: {all_files}")
        for file in all_files:
            local_file_name = str(file)
            if file.is_dir():
                local_file_name += "/"
            s3_key = s3_path_prefix
            s3_key += "".join(local_file_name.split(local_dir_str)[1:])
            LOG.info(f"Uploading {local_file_name} to {s3_bucket}:{s3_key}")
            self.client.upload_file(Filename=local_file_name, Bucket=s3_bucket, Key=s3_key)



S3M = S3Manager()