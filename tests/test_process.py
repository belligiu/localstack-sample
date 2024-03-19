import filecmp
import os
import unittest
from unittest import mock

import boto3
from testcontainers.localstack import LocalStackContainer

from functions import download_file, send_notification

AWS_ACCESS_KEY_ID = "jon"
AWS_SECRET_ACCESS_KEY = "doe"


class TestProcess(unittest.TestCase):

    def test_should_download_s3_file_locally_given_valid_path(self):

        # 1. Preparamos el ambiente de prueba
        # inicializamos el testcontainer con la imagen de LocalStack
        with LocalStackContainer(image="localstack/localstack:3.2.0") as localstack:
            # indicamos que inicie el servicio de S3
            localstack.with_services("s3")

            # le pedimos a Localstack la url ya que debemos mockear la variable de entorno del endpoint de AWS para las pruebas
            endpoint_url = localstack.get_url()

            # mockeamos la variable
            with mock.patch.dict(os.environ, {"AWS_ENDPOINT_URL": endpoint_url}):

                bucket_name = "logs-test-bucket"

                # creamos un cliente de boto3 para poder interactuar con nuestro AWS de LocalStack
                s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                )

                s3_client.create_bucket(Bucket=bucket_name)

                s3_client.upload_file(
                    Bucket=bucket_name,
                    Filename="./tests/resources/logs_test_to_upload.log",
                    Key="logs/logs_test.log",
                )

                # ahora si tenemos listo nuestro ambiente de prueba y podemos ejecutar nuestra función
                
                # 2. Ejecutamos la función que queremos probar
                download_file(
                    output_path="tests/resources/logs_test.log",
                    bucket_file_path="logs/logs_test.log",
                    bucket=bucket_name,
                )

                # 3. Verificamos que el archivo de log se haya descargado a el path que esperamos con el contenido
                self.assertTrue(
                    filecmp.cmp(
                        "tests/resources/logs_test.log",
                        "tests/resources/expected_logs_test.log",
                        shallow=True,
                    )
                )

    def test_should_notify_given_3_error_codes(self):
       
        # 1. Preparamos el ambiente de prueba
        # inicializamos el testcontainer con la imagen de LocalStack
        with LocalStackContainer(image="localstack/localstack:3.2.0") as localstack:

            # indicamos que inicie el servicio de SQS
            localstack.with_services("sqs")

            # le pedimos a Localstack la url ya que debemos mockear la variable de entorno del endpoint de AWS para las pruebas
            endpoint_url = localstack.get_url()

            # mockeamos la variable
            with mock.patch.dict(os.environ, {"AWS_ENDPOINT_URL": endpoint_url}):

                queue_name = "logs-test-queue"

                # creamos un cliente de boto3 para poder interactuar con nuestro AWS de LocalStack
                sqs_client = boto3.client(
                    "sqs",
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                )

                sqs_client.create_queue(QueueName=queue_name)
                queue_url = sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]

                # Construimos una lista de logs para enviar por la cola de mensajes
                logs_to_notify = [
                    {
                        "time": "17/May/2015:08:05:32 +0000",
                        "remote_ip": "93.180.71.3",
                        "remote_user": "-",
                        "request": "GET /downloads/product_1 HTTP/1.1",
                        "response": 304,
                        "bytes": 0,
                        "referrer": "-",
                        "agent": "Debian APT-HTTP/1.3 (0.8.16~exp12ubuntu10.21)",
                    },
                    {
                        "time": "17/May/2015:08:05:23 +0000",
                        "remote_ip": "93.180.71.3",
                        "remote_user": "-",
                        "request": "GET /downloads/product_1 HTTP/1.1",
                        "response": 304,
                        "bytes": 0,
                        "referrer": "-",
                        "agent": "Debian APT-HTTP/1.3 (0.8.16~exp12ubuntu10.21)",
                    },
                    {
                        "time": "17/May/2015:08:05:24 +0000",
                        "remote_ip": "80.91.33.133",
                        "remote_user": "-",
                        "request": "GET /downloads/product_1 HTTP/1.1",
                        "response": 304,
                        "bytes": 0,
                        "referrer": "-",
                        "agent": "Debian APT-HTTP/1.3 (0.8.16~exp12ubuntu10.17)",
                    },
                ]

                # ahora si tenemos listo nuestro ambiente de prueba y podemos ejecutar nuestra función
                
                # 2. Ejecutamos la función que queremos probar
                send_notification(logs_to_notify=logs_to_notify, queue_name=queue_name)

                # le pedimos a la cola 10 mensajes y debería devolvernos 3 (ya que solo mandamos 3 logs para notificar)
                response = sqs_client.receive_message(
                    QueueUrl=queue_url, MaxNumberOfMessages=10
                )
                # 3. verificamos que el largo del array de mensajes sea 3
                self.assertTrue(len(response["Messages"]) == 3)

                # TODO: Comparar el contenido de los mensajes recibidos con el esperado

    def test_should_not_notify_given_0_error_codes(self):
        # lets set up everything to test our download function
        with LocalStackContainer(image="localstack/localstack:3.2.0") as localstack:

            # start s3
            localstack.with_services("sqs")

            # save localstack url to variable
            endpoint_url = localstack.get_url()

            # override the AWS_ENDPOINT_URL environment variable
            with mock.patch.dict(os.environ, {"AWS_ENDPOINT_URL": endpoint_url}):

                queue_name = "logs-test-queue"

                # init boto3 client
                sqs_client = boto3.client(
                    "sqs",
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                )

                # create the queue
                sqs_client.create_queue(QueueName=queue_name)

                # build a sample list of dict to notify
                logs_to_notify = []

                # now lets execute our function!
                send_notification(logs_to_notify=logs_to_notify, queue_name=queue_name)

                queue_url = sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]
                response = sqs_client.receive_message(
                    QueueUrl=queue_url, MaxNumberOfMessages=10
                )
                self.assertTrue(response.get("Messages") is None)