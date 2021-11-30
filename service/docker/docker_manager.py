from typing import List
import docker
from pathlib import Path
import logging
from timeit import default_timer as timer

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
        self.client.containers.prune()

    def prune_images(self):
        # TODO: NOT_SURE replicate docker ps --filter status=exited -q | xargs docker rm
        # Ideally we want to delete all unused images except ubuntu base image - cuz we need it for all images as base
        # delete and then check image list for sanity
        self.client.images.prune(filters={"dangling": True})

    def copy_logs(self, containerId: str, destination_dir: Path):
        pass

    def copy_output(self, containerId: str, destination_dir: Path):
        pass

    def get_exited_containers(self) -> List[str]:
        containters = self.client.containers.list(all=True, filters={"status": "exited"})
        return [container.id for container in containters]


DM = DockerManager()