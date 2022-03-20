from service.aws.rds_manager import RM
from service.deploy_service.task_deploy_request import TaskDeployRequest

def submit_task(task:TaskDeployRequest):
    '''inserting the task first'''
    RM.insert_task(task)
    '''need to insert the next executiont time in tasks_to_schedule'''
    RM.insert_task_schedule(task)