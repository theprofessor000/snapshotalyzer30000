# snapshotalyzer30000
demo project to manage EC2 instances snapshots

## About
This is a demo, and uses boto3 to manage AWS EC2 instance snapshots

## Configure

shotty uses the configuration file created by the AWS cli. e.g.
`aws configure --profile shotty`

## Running 
`pipenv run python shotty/shotty.py`

## Running
`pipenv run python shotty/shotty.py <command> <--project=PROJECT>`
*command* is list, start, or stop
*project* is optional