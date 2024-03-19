#!/bin/bash

# Creamos un bucket de S3
awslocal s3api create-bucket --bucket logs

# Subimos un archivo de logs
awslocal s3api put-object \
    --bucket logs \
    --key logs/20150517.log \
    --body /usr/tmp/resources/20150517.log
