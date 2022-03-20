import logging_init # This needs to be first
import os
import logging
import pymysql
from constants import *

RDS_HOSTNAME="ccdb-rdb-1.cdvaittpurwu.us-east-1.rds.amazonaws.com"
RDS_PORT=3306
RDS_DATABASE="workstream"
LOG = logging.getLogger("TDS")

def cleanup_db():
    conn = pymysql.connect(
            host=RDS_HOSTNAME, 
            port=RDS_PORT, 
            user=os.environ["RDS_USERNAME"], 
            password=os.environ["RDS_PASSWORD"], 
            database=RDS_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True)

    with conn.cursor() as cursor:
        cursor.execute("delete from execution_status", ())
        cursor.execute("delete from execution_info", ())
        cursor.execute("delete from task_execution", ())
        cursor.execute("delete from tasks_to_schedule",())
        cursor.execute("delete from task_request_info", ())
        

    LOG.info("cleaned DB...")

def cleanupp_dirs():
    os.system(f"rm -rf {LOCAL_USER_STAGING_DIR}")
    os.system(f"rm -rf {LOCAL_SERVICE_STAGING_DIR}")
    LOG.info("cleaned dirs")

def cleanup_docker():
    os.system("docker image prune -a -f")
    os.system("docker container prune -f")
    LOG.info("cleaned docker...")

if __name__ == "__main__":
    cleanup_db()
    cleanup_docker()