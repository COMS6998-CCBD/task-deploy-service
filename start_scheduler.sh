#!/usr/bin/env bash
if ! docker info > /dev/null 2>&1; then
  echo "This script uses docker, and it isn't running - please start docker and try again!"
  echo "Run : sudo service docker start"
  exit 1
fi

echo "Loading myvenv"
source ./myvenv/bin/activate

echo "Loading credentials"
source ./credentials/aws_credentials.env
source ./credentials/rds_credentials.env


echo "Starting Scheduler"
python3 schedule_tasks.py