# Task Deploy Service

Contains code for the task deploy service.

Contributors: **Akhil Ravipati**, **Akhil Konda**, **Jainam Shah**, **Srihari Thikkireddy**


## What it does

The Task Deploy Service receives a REST request with a **command** to run, S3 path/prefix to the **input** files needed by the command, and the desired **output** S3 bucket path/prefix to store any output and/or console logs the command might generate.

The commands might also be configured to run according to a cron expression, in which case the details are stored in the database, and polled periodically to execute to execute when it's time.

The overall flow for each such execution is:
- Download the input files from S3 to a temporary directory
- Create a Docket image using a template with the command stamped in and the input files copied into it
- Inject a CPU and memory metrics collecting script into the docker image
- Spin out a container and run the command with the metrics script running in the background
- Once the container exits, copy the console logs, output files, and the metrics out
- Shut the container and clean it up
- Upload the output & metrics generated in the steps above back to S3
- All the while regularly update the Database with the state of the operation


## Code structure
- **task_deploy_service.py** takes care of accepting incoming requests, downloading files, creating the docker image and spinning a container out of it.
- **background_service.py** takes care of listening to recently exited containers, and performing the logs, output and metrics extraction, uploading to S3 and cleaning up the container and all other hanging docker artifacts, images etc. It also polls the Database for any upcoming commands (`next execution time` is stored for each request with a cron expression) and hooks into `task_deploy_service.py` code to execute them.
- **services** Singleton services with self-explanatory interface to respective services needed by the Task Deploy Service.
    - **aws/ec2_manager.py**
    - **aws/rds_manager.py**
    - **aws/s3_manager.py**
    - **docker/docker_manager.py**





## How to start:
- First ensure that the credentials are setup at `./credentials/aws_credentials.env`. These credentials are not part of git. They must be manually setup on the machine where this repo is cloned and expected to be run.
- Source those credentials `source ./credentials/aws_credentials.env`
- Run the server `python3 task_deploy_service.py`
- Sample API json to test:
    ```
        {
            "userId": "akhil-test",
            "uniqueId": "akhil-test-uid",
            "s3_bucket": "ccbd-hw2-frontend",
            "source_s3_prefix": "",
            "destination_s3_prefix": "/out/",
            "command": "python3.9 -c 'print(56789)'",
            "linux_dependencies": ["git", "curl", "python3.9"]
        }
    ```



## EC2 installations
- `sudo yum update -y`
- `sudo yum install git`
- For **Docker** (https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html)
    - `sudo amazon-linux-extras install docker`
    - `sudo yum install docker`
    - `sudo service docker start`
    - `sudo usermod -a -G docker ec2-user`
    - `docker info` (To ensure docker works without having to sudo. Close current session and open new session/terminal first. May require reboot.)
