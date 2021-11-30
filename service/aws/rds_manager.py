from typing import Dict, List, Tuple
import boto3
import pymysql
import os
import uuid
from constants import RDS_HOSTNAME, RDS_PORT, RDS_DATABASE
from service.deploy_service.task_deploy_request import TaskDeployRequest
from service.deploy_service.exec_status import EXEC_STATUS
import logging

LOG = logging.getLogger("TDS")


class RDSConnection:
    def __init__(self, autocommit=True):
        self.conn = None
        self.conn_id = str(uuid.uuid4())
        self.autocommit = autocommit

    def __enter__(self):
        LOG.info(f"Opening RDS connection [{self.conn_id}]")
        self.conn = pymysql.connect(
            host=RDS_HOSTNAME, 
            port=RDS_PORT, 
            user=os.environ["RDS_USERNAME"], 
            password=os.environ["RDS_PASSWORD"], 
            database=RDS_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=self.autocommit)

    def __exit__(self):
        if not self.autocommit:
            LOG.info(f"Commiting RDS connection [{self.conn_id}]")
            self.conn.commit()

        LOG.info(f"Closing RDS connection [{self.conn_id}]")
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            self.conn_id = None


    def execute(self, query: str, values: Tuple) -> Tuple[Dict]:
        results = ()
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            results = cursor.fetchall()
        return results


class RDSManager:
    def __init__(self):
        pass

    def insert_task(tdr: TaskDeployRequest):
        with RDSConnection() as rc:
            rc.execute(
                "insert into task_request_info (task_id, user_id, s3_bucket, source_s3_prefix, destination_s3_prefix, command, linux_dependencies) values (%s, %s, %s, %s, %s, %s, %s)",
                (tdr.task_id, tdr.user_id, tdr.s3_bucket, tdr.source_s3_prefix, tdr.destination_s3_prefix, tdr.command, " ".join(tdr.linux_dependencies)))

    def insert_execution_id(task_id: str, exec_id: str):
        with RDSConnection() as rc:
            rc.execute(
                "insert into task_execution (task_id, exec_id) values (%s, %s)",
                (task_id, exec_id)
            )

    def insert_execution_info(exec_id: str, docker_image_id: str, docker_container_id: str):
        with RDSConnection() as rc:
            rc.execute(
                "insert into execution_info (exec_id, docker_image_id, docker_container_id) values (%s, %s, %s)",
                (exec_id, docker_image_id, docker_container_id)
            )

    def insert_execution_status(exec_id: str, status: EXEC_STATUS):
        with RDSConnection() as rc:
            rc.execute(
                "insert into execution_status (exec_id, status) values (%s, %s)",
                (exec_id, status.value)
            )


RM = RDSManager()