# Task Deploy Service

Contains code for the task deploy service.


## How to start:
- First ensure that the credentials are setup at `./credentials/aws_credentials.env`. These credentials are not part of git. They must be manually setup on the machine where this repo is cloned and expected to be run.
- Source those credentials `source ./credentials/aws_credentials.env`
- Run the server `python3 task_deploy_service.py`
