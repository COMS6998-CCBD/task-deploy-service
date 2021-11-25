# Task Deploy Service

Contains code for the task deploy service.


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
