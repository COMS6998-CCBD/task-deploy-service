import logging_init # This needs to be first
from flask import Flask, request, jsonify
import jsonpickle as jp
from service.deploy_service.task_deploy_request import TaskDeployRequest

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/deploy", methods=["POST"])
def deploy_task():
    request_json = request.json
    request = TaskDeployRequest(**request_json)


if __name__ == '__main__':
    print("***CALLED FROM MAIN***")
    app.run(host="0.0.0.0", port=5001, debug=True)