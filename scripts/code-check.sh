#!/usr/bin/env bash
# Convenience script for running Travis-like checks.

#set -eu
#set -x
{
    readarray -t PY_FILES < <(find lambda_functions ! -path '*node_modules*' ! -path '*.serverless*' -name '*.py')
} &> /dev/null

## Lint and formatting check of all python files in lambdas
pycodestyle "${PY_FILES[@]}"
pylint -j 2 --reports no "${PY_FILES[@]}"
