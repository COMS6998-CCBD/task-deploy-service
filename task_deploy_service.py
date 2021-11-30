import logging_init # This needs to be first
from flask import Flask, jsonify
from flask import request as flask_request
import jsonpickle as jp
from service.deploy_service.task_deploy_request import TaskDeployRequest
from service.deploy_service.deploy import deploy
import logging
import traceback

LOG = logging.getLogger("TDS")

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/deploy", methods=["POST"])
def deploy_task():
    request_json = flask_request.json
    LOG.info(f"JSON request recevied: {request_json}")
    try:
        request = TaskDeployRequest(**request_json)
        deploy(request)
    except Exception as e:
        traceback.print_exc()
        print("\n\n\n\n")
        return {"message": "error"}
    return {"message": "success"}


if __name__ == '__main__':
    print("***CALLED FROM MAIN***")
    app.run(host="0.0.0.0", port=5001, debug=True)