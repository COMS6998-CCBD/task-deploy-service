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
        return self

    def __exit__(self, type, value, traceback):
        if not self.autocommit:
            LOG.info(f"Commiting RDS connection [{self.conn_id}]")
            self.conn.commit()

        LOG.info(f"Closing RDS connection [{self.conn_id}]")
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            self.conn_id = None


    def execute(self, query: str, values: Tuple = ()) -> Tuple[Dict]:
        results = ()
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            results = cursor.fetchall()
        return results


class RDSManager:
    def __init__(self):
        pass

    def insert_task(self, tdr: TaskDeployRequest):
        with RDSConnection() as rc:
            # LOG.info(f"Data is : {(tdr.task_id, tdr.task_name, tdr.user_id, tdr.s3_bucket, tdr.source_s3_prefix, tdr.destination_s3_prefix, tdr.command, ' '.join(tdr.linux_dependencies))}")
            rc.execute(
                "insert into task_request_info (task_id, task_name, user_id, s3_bucket, source_s3_prefix, destination_s3_prefix, command, linux_dependencies) values (%s, %s, %s, %s, %s, %s, %s, %s)",
                (tdr.task_id, tdr.task_name, tdr.user_id, tdr.s3_bucket, tdr.source_s3_prefix, tdr.destination_s3_prefix, tdr.command, " ".join(tdr.linux_dependencies)))

    def insert_execution_id(self, task_id: str, exec_id: str):
        with RDSConnection() as rc:
            rc.execute(
                "insert into task_execution (task_id, exec_id) values (%s, %s)",
                (task_id, exec_id)
            )

    def insert_execution_info(self, exec_id: str, docker_image_id: str, docker_container_id: str):
        with RDSConnection() as rc:
            rc.execute(
                "insert into execution_info (exec_id, docker_image_id, docker_container_id) values (%s, %s, %s)",
                (exec_id, docker_image_id, docker_container_id)
            )

    def insert_execution_status(self, exec_id: str, status: EXEC_STATUS):
        with RDSConnection() as rc:
            rc.execute(
                "insert into execution_status (exec_id, status) values (%s, %s)",
                (exec_id, status.value)
            )

    # gets containers with EXITED as the last status
    def get_exited_executions(self) -> Tuple[Dict]:
        with RDSConnection() as rc:
            res = rc.execute(
                """
                    WITH ordered_statuses AS (
                        SELECT es.*, ROW_NUMBER() OVER (PARTITION BY exec_id ORDER BY modifiedTS DESC) AS rn
                        FROM execution_status AS es
                    )
                    SELECT DISTINCT ei.exec_id, os.status, ei.docker_container_id, tri.task_id, tri.s3_bucket, tri.destination_s3_prefix FROM ordered_statuses os
                    JOIN execution_info ei
                    ON ei.exec_id = os.exec_id 
                    JOIN task_execution te
                    on te.exec_id = ei.exec_id
                    JOIN task_request_info tri
                    ON tri.task_id = te.task_id
                    WHERE os.rn = 1
                    AND os.status='EXITED';

                """
                )
            LOG.info(f"get_exited_executions res from DB: [{res}]")
            return res

    def get_execution_info(self, container_ids: List[str]) -> Tuple[Dict]:
        cids_str = ", ".join([f"'{cid}'" for cid in container_ids])
        QUERY = f"select * from execution_info where docker_container_id in ({cids_str})"
        LOG.info(f"get_execution_info query: {QUERY}")
        with RDSConnection() as rc:
            res = rc.execute(QUERY)
            LOG.info(f"get_execution_info res from DB: [{res}]")
            return res


    def test_the_db(self) -> Tuple[Dict]:
        with RDSConnection() as rc:
            res = rc.execute(
                "select * from execution_info")
            LOG.info(f"test_the_db res from DB: [{res}]")
            return res


RM = RDSManager()