from re import LOCALE
from typing import List
from service.deploy_service.task_deploy_request import TaskDeployRequest
from service.aws.s3_manager import S3M
from constants import *
from pathlib import Path
import shutil as sh
import shlex
import os
import logging
from service.docker.docker_manager import DM

LOG = logging.getLogger("TDS")

def prepare_dockerfile(command: str, linux_deps: List[str], files_dir_path: str, uniqueId: str) -> Path:
    srcPath = Path(DOCKER_TEMPLATE_FILEPATH)
    dstPath = Path(f"{LOCAL_USER_STAGING_DIR}/{uniqueId}/Dockerfile")
    os.makedirs(dstPath.parent, exist_ok=True)
    sh.copy(srcPath, dstPath)

    lines = []
    with open(dstPath, "r") as f:
        lines = f.readlines()
    
    transformed_lines = []
    for line in lines:
        if "{LINUX_DEPENDENCIES}" in line:
            # Do NOT add this line if there are no deps
            if linux_deps is None or len(linux_deps) == 0:
                continue 
            else:
                line = line.replace("{LINUX_DEPENDENCIES}", " ".join(linux_deps))

        if "{SOURCE_DIR_PATH}" in line:
            line = line.replace("{SOURCE_DIR_PATH}", files_dir_path)

        if "{DESTINATION_DIR_PATH}" in line:
            line = line.replace("{DESTINATION_DIR_PATH}", ".")

        if "{COMMAND_ARRAY}" in line:
            cmd_arr = shlex.split(command)
            cmd = ", ".join([f'"{cmd}"' for cmd in cmd_arr])
            cmd = f"[{cmd}]"
            line = line.replace("{COMMAND_ARRAY}", cmd)
            
        transformed_lines.append(line)

    with open(dstPath, "w") as f:
        f.writelines(transformed_lines)

    LOG.info(f"Wrote Dockerfile for uniqueId: {uniqueId} as follows: \n{''.join(transformed_lines)}")
    return dstPath


def deploy(request: TaskDeployRequest):
    local_user_dir_str = LOCAL_USER_STAGING_DIR + "/" + request.uniqueId
    local_user_dir_path = Path(local_user_dir_str)

    sh.rmtree(local_user_dir_path)
    S3M.s3_to_local(request.s3_bucket, request.source_s3_prefix, local_user_dir_path.joinpath("files"))

    dockerfile_filepath = prepare_dockerfile(request.command, request.linux_dependencies, "files", request.uniqueId)
    imageId = DM.create_image(dockerfile_filepath=dockerfile_filepath, tag=request.uniqueId)
    LOG.info(f"docker image id: {imageId}")
    containerId = DM.run(imageId)
    LOG.info(f"docker container id: {containerId}")
    # then something about stats
