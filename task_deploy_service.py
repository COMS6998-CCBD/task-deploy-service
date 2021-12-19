import logging_init # This needs to be first
from flask import Flask, jsonify
from flask import request as flask_request
import jsonpickle as jp
from service.deploy_service.task_deploy_request import TaskDeployRequest
from service.deploy_service.deploy import deploy
import logging
import traceback
from service.deploy_service.submit_task import submit_task
LOG = logging.getLogger("TDS")

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
@app.route("/submit_task",methods = ["POST"])
def submit_new_task():
    request_json = flask_request.json
    LOG.info(f"JSON request recevied: {request_json}")
    try:
        '''using previous task class but no exec id this time'''
        if 'exec_id' not in request_json:
            request_json['exec_id'] = None
        request = TaskDeployRequest(**request_json)
        LOG.info(f"submit_task request = {request.cron_expression}")
        submit_task(request)
    except Exception as e:
        traceback.print_exc()
        print("\n\n\n\n")
        return {"message": "error"}
    return {"message": "success"}

@app.route("/deploy", methods=["POST"])
def deploy_task():
    request_json = flask_request.json
    LOG.info(f"JSON request recevied: {request_json}")
    # LOG.info(f"JSON request data recevied: {flask_request.data}")
    try:
        request = TaskDeployRequest(**request_json)
        deploy(request)
    except Exception as e:
        traceback.print_exc()
        print("\n\n\n\n")
        return {"message": "error"}
    return {"message": "success"}


# def start_background_services():
#     print("***STARTING BACKGROUND SERVICES****")


if __name__ == '__main__':
    print("***CALLED FROM MAIN***")
    # start_background_services()
    app.run(host="0.0.0.0", port=5001, debug=False)