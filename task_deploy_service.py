import logging_init # This needs to be first
import logging
from flask import Flask
import datetime
import logging
import os
import colorlog

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/deploy", methods=["POST"])
def deploy_task():
    pass

def init():
    

if __name__ == '__main__':
    print("***CALLED FROM MAIN***")
    app.run(host="0.0.0.0", port=5001, debug=True)