import time
import csv
from confluent_kafka import Producer
import json

# Configuración del producer
conf = {
    'bootstrap.servers': 'localhost:9092',  # Cambia por la dirección de tu broker
    'client.id': 'sensor_data_producer'
}

producer = Producer(conf)

# Función de callback para manejar la confirmación de envío
def delivery_report(err, msg):
    if err is not None:
        print(f"Error al enviar mensaje: {err}")
    else:
        print(f"Mensaje enviado a {msg.topic()} [partición {msg.partition()}]")

# Lee el archivo CSV y envía datos al topic
def send_csv_to_kafka(file_path, topic):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Serializa la fila en formato JSON (puedes ajustarlo según la estructura de tu CSV)
            message = json.dumps(row)
            producer.produce(topic, key=None, value=message, callback=delivery_report)
            producer.flush()  # Asegura que el mensaje se envíe
            print(f"Enviando: {message}")
            time.sleep(3)  # Espera de 3 segundos entre mensajes

if __name__ == "__main__":
    csv_file_path = "Data_final.csv"  # Cambia a la ruta de tu archivo CSV
    kafka_topic = "sensor_data_1"  # Nombre del topic
    send_csv_to_kafka(csv_file_path, kafka_topic)