import docker
from pathlib import Path

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()

    def create_image(self, dockerfile_path: Path):
        pass

    def delete_image(self, imageId: str):
        pass

    def run(self, imageId: str):
        pass

    def copy_logs(self, imageId: str, destination_dir: Path):
        pass

    def copy_output(self, imageId: str, destination_dir: Path):
        pass


DM = DockerManager()