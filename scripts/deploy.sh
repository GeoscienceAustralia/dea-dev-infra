#!/usr/bin/env bash

npm install -g serverless

cd lambda_functions/manage_ec2/ && npm install

serverless config credentials --provider aws --key "${AWS_ACCESS_KEY_ID}" --secret "${AWS_SECRET_ACCESS_KEY}" --profile devProfile
serverless deploy -v --stage dev