from pathlib import Path

S3 = "S3"
LOCAL_USER_STAGING_DIR = "/var/tmp/task-deploy-service/user"
LOCAL_SERVICE_STAGING_DIR = "/var/tmp/task-deploy-service/service"

# Dynamically resolve this to avoid problems
DOCKER_TEMPLATE_FILEPATH = "./deploy_artifacts/Dockerfile.template"
assert Path(DOCKER_TEMPLATE_FILEPATH).exists()