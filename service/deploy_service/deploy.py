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
from service.aws.rds_manager import RM
import uuid
from service.deploy_service.exec_status import EXEC_STATUS
import zipfile

LOG = logging.getLogger("TDS")

def prepare_dockerfile(command: str, linux_deps: List[str], files_dir_path: str, exec_id: str) -> Path:
    srcPath = Path(DOCKER_TEMPLATE_FILEPATH)
    dstPath = Path(f"{LOCAL_USER_STAGING_DIR}/{exec_id}/Dockerfile")
    os.makedirs(dstPath.parent, exist_ok=True)
    sh.copy(srcPath, dstPath)

    lines = []
    with open(dstPath, "r") as f:
        lines = f.readlines()
    
    transformed_lines = []
    for line in lines:
        LOG.debug(f"Before line: [{line}]")
        if "{LINUX_DEPENDENCIES}" in line:
            # Do NOT add this line if there are no deps
            if linux_deps is None or len(linux_deps) == 0:
                continue 
            else:
                line = line.replace("{LINUX_DEPENDENCIES}", " ".join(linux_deps))

        if "{SOURCE_DIR_PATH}" in line:
            LOG.info(f"replacing source with [{files_dir_path}]")
            line = line.replace("{SOURCE_DIR_PATH}", files_dir_path)

        if "{DESTINATION_DIR_PATH}" in line:
            line = line.replace("{DESTINATION_DIR_PATH}", ".")

        if "{COMMAND_ARRAY}" in line:
            cmd_arr = shlex.split(command)
            cmd = ", ".join([f'"{cmd}"' for cmd in cmd_arr])
            cmd = f"[{cmd}]"
            line = line.replace("{COMMAND_ARRAY}", cmd)

        if "{COMMAND}" in line:
            line = line.replace("{COMMAND}", command)
            
        LOG.debug(f"After line: [{line}]")
        transformed_lines.append(line)

    with open(dstPath, "w") as f:
        f.writelines(transformed_lines)

    LOG.info(f"Wrote Dockerfile for uniqueId: {exec_id} as follows: \n{''.join(transformed_lines)}")
    return dstPath


def unzip_files(local_user_files_dir_path: Path):
    zip_files = list(local_user_files_dir_path.rglob("*.zip")) + list(local_user_files_dir_path.rglob("*.7z"))
    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            # extract_dir = zip_file.parent.joinpath(zip_file.stem)
            LOG.info(f"Extracting {zip_file} to {zip_file.parent}")
            zip_ref.extractall(zip_file.parent)
        zip_file.unlink()


def deploy(request: TaskDeployRequest):
    RM.insert_task(request)
    RM.insert_execution_id(request.task_id, request.exec_id)
    LOG.info(f"linked task_id [{request.task_id}] to exec_id [{request.exec_id}]")

    local_user_dir_str = LOCAL_USER_STAGING_DIR + "/" + request.exec_id
    local_user_dir_path = Path(local_user_dir_str)
    sh.rmtree(local_user_dir_path, ignore_errors=True)

    local_user_files_dir_path = local_user_dir_path.joinpath("files")
    S3M.s3_to_local(request.s3_bucket, request.source_s3_prefix, local_user_files_dir_path)
    unzip_files(local_user_files_dir_path)

    

    dockerfile_filepath = prepare_dockerfile(request.command, request.linux_dependencies, "files", request.exec_id)
    imageId = DM.create_image(dockerfile_filepath=dockerfile_filepath, tag=request.exec_id)
    LOG.info(f"for exec_id: [{request.exec_id}] docker image id: [{imageId}]")
    RM.insert_execution_status(request.exec_id, EXEC_STATUS.CREATED)

    containerId = DM.run(imageId)
    LOG.info(f"for exec_id: [{request.exec_id}] docker container id: [{containerId}]")
    RM.insert_execution_info(request.exec_id, imageId, containerId)
    RM.insert_execution_status(request.exec_id, EXEC_STATUS.STARTED)
