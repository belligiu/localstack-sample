from functions import download_file, transform, send_notification

# primero descargamos nuestro archivo de logs de S3
download_file(
    output_path="resources/INPUT_FILE.log",
    bucket_file_path="logs/20150517.log",
    bucket="logs",
)

# Aplicamos algunas transformaciones a nuestro archivo, lo guardamos local e
# identificamos cuáles logs debemos notificar para el siguiente paso
logs_to_notify = transform(
    file_name="INPUT_FILE.log", local_path="./resources/OUTPUT_FILE.csv"
)

# Mandamos las notificaciones para los logs que identificamos
send_notification(logs_to_notify=logs_to_notify, queue_name="logs-queue")
