from pathlib import Path
import shutil
import os

S3 = "S3"
LOCAL_USER_STAGING_DIR = "/var/tmp/task-deploy-service/user"
LOCAL_SERVICE_STAGING_DIR = "/var/tmp/task-deploy-service/service"

# ensure that the dirs are present at startup
os.makedirs(LOCAL_USER_STAGING_DIR, exist_ok=True)
os.makedirs(LOCAL_SERVICE_STAGING_DIR, exist_ok=True)

# Dynamically resolve this to avoid problems
DOCKER_TEMPLATE_FILEPATH = "./deploy_artifacts/Dockerfile.template"
assert Path(DOCKER_TEMPLATE_FILEPATH).exists()


RDS_HOSTNAME="ccdb-rdb-1.cdvaittpurwu.us-east-1.rds.amazonaws.com"
RDS_PORT=3306
RDS_DATABASE="workstream"