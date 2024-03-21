import csv
import json
import logging
import os

import boto3

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def download_file(bucket_file_path: str, bucket: str, output_path: str):
    session = boto3.Session()

    s3 = session.client(service_name="s3")
    logging.info(
        f"Downloading file from S3 - AWS Endpoint URL:{os.getenv('AWS_ENDPOINT_URL')}"
    )

    s3.download_file(bucket, bucket_file_path, output_path)


def transform(file_name: str, local_path: str):
    output = []
    logs_to_notify = []
    logging.info("Transforming file and identifying logs to notify.")
    with open(f"./resources/{file_name}") as f:
        for line in f:
            output_line = []
            log: dict = json.loads(line)
            output_line.append(log["time"])
            output_line.append(log["remote_ip"])
            output_line.append(
                log["remote_user"] if log["remote_user"] != "-" else None
            )
            # Aquí deberíamos implementar validaciones de calidad sobre los datos generados
            # para eso podemos usar librerías como GreatExpectations, Pydq o
            # herramientas más avanzadas con inteligencia artificial como Rudol
            if log["response"] != 200:
                logs_to_notify.append(log)
            output.append(output_line)

    logging.info("Writing output to csv.")
    with open(local_path, "w") as f:
        writer = csv.writer(f)
        writer.writerows(output)
    logging.info("Finished transforming logs data.")
    return logs_to_notify


def send_notification(logs_to_notify: list[dict], queue_name: str):
    session = boto3.Session()

    sqs = session.client(service_name="sqs")

    queue = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
    logging.info(f"Sending messages to the queue {queue}.")
    for log in logs_to_notify:
        sqs.send_message(
            QueueUrl=queue,
            MessageBody=f"There was an error with the access to Elastic.The error code was: {log['response']}.The access url was: {log['request']}. The IP was: {log['remote_ip']}. Please alert someone.",
        )
    logging.info("Finished sending messages.")
