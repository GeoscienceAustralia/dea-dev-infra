#!/usr/bin/env bash

set -eu

cd "$PWD"/lambda_functions/manage_ec2 && npm install
serverless deploy -v -s dev