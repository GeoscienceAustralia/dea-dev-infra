#!/usr/bin/env bash

# Configure serverless AWS custom profile settings.
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_DEFAULT_REGION are expected to be
# configured in travis project web settings
serverless config credentials --provider aws --key $AWS_ACCESS_KEY_ID --secret $AWS_SECRET_ACCESS_KEY --profile devProfile --overwrite
cd lambda_functions/manage_ec2/ && npm install
serverless deploy -v --stage dev