#!/usr/bin/env bash
cd /home/ec2-user/workstream/task-deploy-service/
eval `ssh-agent`
sleep 2
ssh-add /home/ec2-user/.ssh/id_ed25519_akhil
sleep 2
ssh-keyscan github.com >> ~/.ssh/known_hosts
git checkout AK_branch
git pull origin AK_branch
source ./myvenv/bin/activate
pip install -r requirements.txt
sudo service docker start
./start_server.sh </dev/null > server_output.log 2>&1 &
./start_background_service.sh </dev/null > background_logs.log 2>&1 &
