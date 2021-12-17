import logging_init # This needs to be first

import logging
from service.aws.rds_manager import RM
import traceback
import time
from service.deploy_service.task_deploy_request import TaskDeployRequest
from service.deploy_service.deploy import deploy
import uuid
LOG = logging.getLogger("TDS")

def get_req_task_details(task_full_details):
    req_fields = ['user_id','task_id','task_name','exec_id','s3_bucket','source_s3_prefix','command','cron_expression','linux_dependencies']
    req_dict = {}
    for field in req_fields:
        req_dict[field] = task_full_details[field]
    return req_dict

def schedule():
    '''get all the jobs to be scheduled'''
    task_ids = RM.get_all_tasks_to_schedule()
    for task_id_dict in task_ids:
        task_id = task_id_dict['task_id']
        '''get single task details and deploy the job'''
        task_full_details = RM.get_task_details(task_id)[0]
        exec_id = str(uuid.uuid4())
        # task_full_details['destination_s3_prefix'] =  task_id+'/'+exec_id+'/output'
        task_full_details['exec_id'] = exec_id
        task_details = get_req_task_details(task_full_details)
        cron_expr = task_details['cron_expression']
        LOG.info(f"scheduling task_details: {task_details}")
        task_deployed = False
        task_details['exec_id'] = exec_id 
        request = TaskDeployRequest(**task_details)
        try:
            deploy(request)
            task_deployed = True
        except Exception as e:
            traceback.print_exc()
            print("\n\n\n\n")
            LOG.error(f"deployment failed for task_id = {task_id}")
        
        if(task_deployed):
            RM.delete_task_schedule(task_id)
            LOG.info(f"task_id = {task_id} deleted task_full_details = {task_full_details}")

        '''TODO: might have make both task_id,scheduling time are primary keys'''    
        if(task_deployed and cron_expr):
            RM.insert_task_schedule(request)
            LOG.info(f" insert next time task_id = {task_id} ")


        
    return {"message": "success"}

if __name__ == "__main__":
    while True:
        try:
           schedule()
        except Exception as e:
            traceback.print_exc()
            print("\n\n\n\n")
        LOG.info("sleeping.....")
        time.sleep(10)
        LOG.info("woke up.....")