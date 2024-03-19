#!/bin/bash

# Creamos una cola de mensajes
awslocal sqs create-queue \
    --queue-name logs-queue
