# dea-dev-infra
This git repo manages Digital Earth Australia dev infrastructure

_It is made up of:_
- AWS Lambda functions in `lambda_functions/`

## Lambda Functions
### manage_ec2:
**Purpose:** This lambda function schedule - start/stop - tagged EC2 instances.<br/>
**Deploy:** `serverless deploy -v --stage dev`<br/>
**Configuration:** This lambda function supports following Environment variables - <br/>
   - SCHEDULE_TAG: Tag used for filtering EC2 instances.
   - SCHEDULE_START_TIME: EC2 instance start time. Provide a time in 24 hours clock. Default is set to `07:00`.
   - SCHEDULE_STOP_TIME: EC2 instance stop time. Provide a time in 24 hours clock. Default is set to `18:00`.
   - TIME_ZONE: Define time zone used for start and stop instances. Default is set to `Australia/Sydney`.
  
