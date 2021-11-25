from typing import List
from task_deploy_request import TaskDeployRequest
from aws.s3_manager import S3M
from constants import *
from pathlib import Path
import shutil as sh
import shlex
import os
import logging
from docker.docker_manager import DM

LOG = logging.getLogger("TDS")

def prepare_dockerfile(command: str, linux_deps: List[str], source_dir: str, uniqueId: str) -> Path:
    srcPath = Path(DOCKER_TEMPLATE_FILEPATH)
    dstPath = Path(f"{LOCAL_SERVICE_STAGING_DIR}/{uniqueId}/Dockerfile")
    sh.copy(srcPath, dstPath)

    lines = []
    with open(dstPath, "r") as f:
        lines = f.readlines()
    
    transformed_lines = []
    for line in lines:
        transformed_line = line
        if "{LINUX_DEPENDENCIES}" in line:
            # Do NOT add this line if there are no deps
            if linux_deps is None or len(linux_deps) == 0:
                continue 
            else:
                transformed_line = line.replace("{LINUX_DEPENDENCIES}", " ".join(linux_deps))
        elif "{SOURCE_DIR_PATH}" in line:
            transformed_line = line.replace("{SOURCE_DIR_PATH}", source_dir)
        elif "{DESTINATION_DIR_PATH}" in line:
            transformed_line = line.replace("{DESTINATION_DIR_PATH}", ".")
        elif "{COMMAND_ARRAY}" in line:
            transformed_line = line.replace("{COMMAND_ARRAY}", str(shlex.split(command)))
        transformed_lines.append(transformed_line)

    with open(dstPath, "w") as f:
        f.writelines(transformed_lines)

    LOG.info(f"Wrote Dockerfile for uniqueId: {uniqueId} as follows: \n{''.join(transformed_lines)}")
    return dstPath


def deploy(request: TaskDeployRequest):
    local_user_dir = LOCAL_USER_STAGING_DIR + "/" + request.uniqueId
    S3M.s3_to_local(request.s3_bucket, request.source_s3_path, local_user_dir)
    dockerfile_filepath = prepare_dockerfile(request.command, request.linux_dependencies, local_user_dir, request.uniqueId)
    imageId = DM.create_image(dockerfile_filepath)
    containerId = DM.run(imageId)
    # then something about stats
