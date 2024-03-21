# localstack-sample
Repositorio con el código de la charla "Desarrolla en la nube con confianza:  Aprende a probar tus integraciones con AWS"

## Prerequisitos
Para ejecutar este repositorio necesitas: 
* Docker
* Conda (recomendado)

## Para empezar a usar este repo
Solo necesitas hacer estos pasos la primera vez que vayas a usar este repo
1. Abrí una terminal
2. Crea un nuevo ambiente con python 3.11 (al menos)

```bash
conda create --name charla-aws python=3.11.8
conda activate charla-aws
```

3. Ejecuta `pip install -r requirements.txt` para instalar las librerías necesarias
4. Ejecuta `docker compose up` para encender el contenedor de LocalStack 

### La próxima vez que uses este repositorio
Solo necesitas ejecutar activar el ambiente que creaste con `conda activate charla-aws` y ejecutar `docker compose up` para encender el contenedor de LocalStack.

## ¿Qué tiene este repositorio? 
En `functions.py` vas a encontrar 3 funciones: 
1. `download_file`: descarga un archivo de logs de un bucket de S3.
2. `transform`: aplica transformaciones sobre el archivo descargado y lo vuelve a guardar como `.csv`. Además, devuelve una lista de request que devolvieron un código que no haya sido 200.
3. `send_notification`: envía un mensaje a una cola de SQS por cada log que recibe como parametro. 

Podes ejecutar las funciones de `functions.py` ejecutando el archivo `main.py`.
El código esta preparado para que todo se ejecute apuntando a *LocalStack* y no a los servicios de Amazon Productivo.

## Los tests (¡no te los olvides!)
Para los tests este repositorio utiliza *TestContainers* para correr *LocalStack* durante los tests de integración. 
Podes ejecutarlos desde la pestaña de Pruebas de tu Visual Studio. 