from typing import Dict, List, Tuple
import boto3
import pymysql
import os
import uuid
from constants import RDS_HOSTNAME, RDS_PORT, RDS_DATABASE
from service.deploy_service.task_deploy_request import TaskDeployRequest
from service.deploy_service.exec_status import EXEC_STATUS
import logging
import datetime
import croniter

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

    def delete_task_schedule(self,task_id):
        with RDSConnection() as rc:
            result = rc.execute('delete from tasks_to_schedule as ts where ts.task_id = %s',task_id)
            LOG.info(f"result = {result}")

    def get_task_details(self,task_id):
        with RDSConnection() as rc:
            LOG.info(f"get task task_id = {task_id}")
            # LOG.info(f'select * from task_request_info as tr where tr.task_id = {task_id}')
            result = rc.execute('select * from task_request_info as tr where tr.task_id = %s',task_id)
            LOG.info(f"task details result = {result}")
            return result

    def get_all_tasks_to_schedule(self, ec2id: str) -> Tuple[Dict]:
        with RDSConnection() as rc:
             cur_time = datetime.datetime.now()
             LOG.info(f"cur_time = {cur_time}")
             result = rc.execute("select ts.task_id from tasks_to_schedule as ts where ts.next_schedule_time<=%s and ts.ec2id=%s", (cur_time, ec2id))
             LOG.info(f"result = {result}")
             return result

    def insert_task_schedule(self,tdr:TaskDeployRequest):
        with RDSConnection() as rc:
            cur_time = datetime.datetime.now()
            if tdr.cron_expression:
                LOG.info(f"inside insert task schedule cronexpor = {tdr.cron_expression}")
                cron = croniter.croniter(tdr.cron_expression, cur_time)
                scheduled_time = cron.get_next(datetime.datetime)
            else:
                '''for non-cron jobs inserting the next scheduled time as right away to get picked up fast'''
                scheduled_time = cur_time #+datetime.timedelta(minutes=1)
            
            rc.execute("insert into tasks_to_schedule(task_id,next_schedule_time) values(%s,%s)",(tdr.task_id,scheduled_time))
            

    def insert_task(self, tdr: TaskDeployRequest):
        with RDSConnection() as rc:
            # LOG.info(f"Data is : {(tdr.task_id, tdr.task_name, tdr.user_id, tdr.s3_bucket, tdr.source_s3_prefix, tdr.destination_s3_prefix, tdr.command, ' '.join(tdr.linux_dependencies))}")
            if tdr.cron_expression:
                LOG.info(f" linux_dependencies = {tdr.linux_dependencies}")
                rc.execute(
                "insert into task_request_info (task_id, task_name, user_id, s3_bucket, source_s3_prefix, command, linux_dependencies,cron_expression) values (%s, %s, %s, %s, %s, %s, %s, %s)",
                (tdr.task_id, tdr.task_name, tdr.user_id, tdr.s3_bucket, tdr.source_s3_prefix, tdr.command, " ".join(tdr.linux_dependencies),tdr.cron_expression))
            else:
                rc.execute(
                "insert into task_request_info (task_id, task_name, user_id, s3_bucket, source_s3_prefix, command, linux_dependencies) values (%s, %s, %s, %s, %s, %s, %s)",
                (tdr.task_id, tdr.task_name, tdr.user_id, tdr.s3_bucket, tdr.source_s3_prefix, tdr.command, " ".join(tdr.linux_dependencies)))

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
                    SELECT DISTINCT ei.exec_id, os.status, ei.docker_container_id, tri.task_id, tri.s3_bucket FROM ordered_statuses os
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
            # LOG.info(f"get_exited_executions res from DB: [{res}]")
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


    def update_task_to_schedule(self, ec2id: str) -> Tuple[Dict]:
        with RDSConnection() as rc:
            query = """
                    update tasks_to_schedule set ec2id=%s where task_id in (
                        select task_id from (
                            select task_id from tasks_to_schedule as ts where ts.ec2id is null limit 1
                        ) tmp 
                    )
                """
            LOG.info(f"QUERY to execute: {query} with ec2id: {ec2id}")
            res = rc.execute(query, (ec2id))
            LOG.info(f"updated task to schedule with {ec2id}, results: {res}")
            return res


RM = RDSManager()