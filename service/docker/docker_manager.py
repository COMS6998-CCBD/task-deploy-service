import docker
from pathlib import Path
import logging

LOG = logging.getLogger("TDS")

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.default_build_args = {
            "memory": 100*1024*1024, # need to scale as per user's data -> limit user data to 50mb for now
            "cpus": 0.25
        }
        self.default_restart_policy = {
            "Name": "on-failure",
            "MaximumRetryCount": 2
        }

    def create_image(self, dockerfile_filepath: Path, tag: str) -> str:
        imageObj = self.client.images.build(
            dockerfile = str(dockerfile_filepath),
            container_limits=self.default_build_args)
        LOG.info(f"Created image with id: {imageObj.id}")
        return imageObj.id

    def delete_image(self, imageId: str):
        self.client.remove(image=imageId)

    def run(self, imageId: str) -> str:
        containerObj = self.client.run(
            image=imageId, 
            auto_remove=True, 
            remove=False, # check this
            restart_policy = self.default_restart_policy,
            detach=True # returns container object
        )
        LOG.info(f"Initiated container run -> containerObj with id: {containerObj.id}")
        return containerObj.id

    def prune(self):
        self.client.prune()

    def copy_logs(self, imageId: str, destination_dir: Path):
        pass

    def copy_output(self, imageId: str, destination_dir: Path):
        pass


DM = DockerManager()