from typing import List
import docker
from pathlib import Path
import logging
from timeit import default_timer as timer
from constants import DOCKER_OUTPUT_DIR

LOG = logging.getLogger("TDS")

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.default_build_args = {
            "memory": 100*1024*1024, # need to scale as per user's data -> limit user data to 50mb for now
            "cpushares": 256
        }
        self.default_restart_policy = {
            "Name": "on-failure",
            "MaximumRetryCount": 2
        }

    def create_image(self, dockerfile_filepath: Path, tag: str) -> str:
        LOG.info(f"Creating image using [{dockerfile_filepath}] tagged: [{tag}]")
        start_time = timer()
        imageObj, log_generator = self.client.images.build(
            path = str(dockerfile_filepath.parent),
            container_limits=self.default_build_args,
            tag=tag,
            timeout=600,
            rm=True)
            #nocache=True)
        duration = timer() - start_time
        image_id = imageObj.id
        image_id = image_id.replace("sha256:", "")
        LOG.info(f"Created image with id: [{image_id}] with tags: [{imageObj.tags}]. Time taken: {duration:.4f}(s)")
        return image_id 

    def delete_image(self, imageId: str):
        self.client.images.remove(image=imageId)

    def run(self, imageId: str) -> str:
        LOG.info(f"Running image : {imageId}")
        containerObj = self.client.containers.run(
            image=imageId, 
            #auto_remove=True, 
            #remove=False, # check this
            #restart_policy = self.default_restart_policy,
            detach=True # returns container object
        )
        LOG.info(f"Initiated container run -> containerObj with id: [{containerObj.id}], imageId: [{containerObj.image.id}]")
        return containerObj.id

    def prune_containers(self):
        # remove unused containers
        LOG.info(f"Pruning containers")
        self.client.containers.prune()

    def prune_images(self):
        # TODO: NOT_SURE replicate docker ps --filter status=exited -q | xargs docker rm
        # Ideally we want to delete all unused images except ubuntu base image - cuz we need it for all images as base
        # delete and then check image list for sanity
        self.client.images.prune()

    def copy_logs_to_file(self, containerId: str, destination_output_filepath: Path):
        LOG.info(f"starting copy_logs_to_file for containerId: [{containerId}] and destination_output_path: [{destination_output_filepath}]")
        container = self.client.containers.get(containerId)
        logs_str = container.logs(stdout=True, stderr=True, timestamps=True)
        LOG.info(f"got log str: [{logs_str}]")
        destination_output_filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(destination_output_filepath, "wb+") as f:
            f.write(logs_str)
        LOG.info(f"done copy_logs_to_file")

    def copy_output_to_file(self, containerId: str, destination_output_filepath: Path):
        LOG.info(f"starting copy_output_to_file for containerId: [{containerId}] and destination_output_path: [{destination_output_filepath}]")
        container = self.client.containers.get(containerId)
        raw_stream, stats = container.get_archive(DOCKER_OUTPUT_DIR)
        LOG.info(f"Got stats: [{stats}]")
        destination_output_filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(destination_output_filepath, "wb+") as f:
            for chunk in raw_stream:
                f.write(chunk)
        LOG.info(f"done copy_output_to_file")

    def get_exited_containers(self) -> List[str]:
        containters = self.client.containers.list(all=True, filters={"status": "exited"})
        exited_ids = [container.id for container in containters]
        LOG.info(f"Exited containers are: [{exited_ids}]")
        return exited_ids

    def remove_containers(self, container_ids: List[str]):
        LOG.info(f"removing containers: [{container_ids}]")
        for container_id in container_ids:
            self.client.containers.get(container_id).remove()
            LOG.info(f"\tRemoved container: [{container_id}]")



DM = DockerManager()