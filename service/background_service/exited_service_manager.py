from service.aws.rds_manager import RM
from service.docker.docker_manager import DM
from service.aws.s3_manager import S3M
from service.deploy_service.exec_status import EXEC_STATUS
from constants import LOCAL_USER_STAGING_DIR
from pathlib import Path
import shutil as sh
import logging

LOG = logging.getLogger("TDS")

class ExitServiceManager:

    def main(self):
        # TEST - WORKS
        # test_res = RM.test_the_db()

        # Get all exited containers from DB
        exited_executions = RM.get_exited_executions()
        db_exited_cids = set([exited_execution["docker_container_id"] for exited_execution in exited_executions])
        LOG.info(f"DB exited executions: [{db_exited_cids}]")

        # Mark newly exited containers as exited, if not already marked as EXITED in DB.
        docker_all_exited_cids = DM.get_exited_containers()
        docker_newly_exited_cids = [cid for cid in docker_all_exited_cids if cid not in db_exited_cids]
        docker_newly_exited_cids = docker_all_exited_cids

        if len(docker_newly_exited_cids) != 0:
            db_resp = RM.get_execution_info(docker_newly_exited_cids)
            cid_execid_map = {resp["docker_container_id"]: resp["exec_id"] for resp in db_resp}

            LOG.info(f"Newly exited docker container ids: [{docker_all_exited_cids}]")
            for cid in docker_newly_exited_cids:
                if cid not in cid_execid_map:
                    LOG.warning(f"ContainerID [{cid}] not present in the cid_execid_map, ignoring it")
                    continue
                RM.insert_execution_status(cid_execid_map[cid], EXEC_STATUS.EXITED)
                LOG.info(f"\tInserted EXITED for [{cid}]")
            

            # Copy output and files from exited containers to local path
            # Fetch EXITED executions from DB again just liks that - we'll optimze later
            LOG.info(f"Beginning the copy process")
            exited_executions = RM.get_exited_executions()
            for exited_execution in exited_executions:
                exec_id = exited_execution["exec_id"]
                docker_container_id = exited_execution["docker_container_id"]
                destination_prefix = exited_execution["destination_s3_prefix"]
                s3bucket = exited_execution["s3_bucket"]

                if docker_container_id not in docker_all_exited_cids:
                    LOG.warning(f"Docker container {docker_container_id} from DB is not present in ec2!!")
                    continue

                LOG.info(f"Working copy for exited_container exec_id: [{exec_id}], container_id: [{docker_container_id}], destination_prefix: [{destination_prefix}] in s3 bucket: [{s3bucket}]")

                local_user_dir_str = LOCAL_USER_STAGING_DIR + "/" + exec_id + "/output" 
                local_user_dir_path = Path(local_user_dir_str)
                LOG.info(f"Removing dir [{local_user_dir_str}]")
                sh.rmtree(local_user_dir_path, ignore_errors=True)

                DM.copy_logs_to_file(docker_container_id, local_user_dir_path.joinpath("stdout.txt"))
                DM.copy_output_to_file(docker_container_id, local_user_dir_path.joinpath("output.tar"))
                
                # CURR: Let's try this in next iteration - let's keep everything local
                S3M.local_to_s3(s3bucket, destination_prefix, local_user_dir_path)
                RM.insert_execution_status(cid_execid_map[cid], EXEC_STATUS.COPIED)
                LOG.info(f"Inserted COPIED for [{cid}]")

        
            # Remove the containers
            # TODO: improve status updates to a single SQL query
            # CURR: 
            DM.remove_containers(docker_all_exited_cids)
            LOG.info(f"Marking all docker exited containers as DELETED: [{docker_all_exited_cids}]")
            for cid in docker_all_exited_cids:
                # CURR: 
                RM.insert_execution_status(cid_execid_map[cid], EXEC_STATUS.DELETED)
                LOG.info(f"\tInserted DELETED for [{cid}]")

        # Remove dangling images
        # TODO: Add opt for except UBUNTU
        # CURR: 
        DM.prune_images()


EM = ExitServiceManager()