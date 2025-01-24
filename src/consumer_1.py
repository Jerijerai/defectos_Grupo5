from confluent_kafka import Consumer, KafkaError
import pandas as pd
import pickle
import json
import re
from influxdb_client import InfluxDBClient, Point
from influxdb_client.write_api import SYNCHRONOUS

client = InfluxDBClient(host = 'http://localhost:8086', token = "dj7TiigIkeQHcNd3VmprVWGor0ClAGQhUpEC8EiWuwfVQbfOnPwIgl0zLasmbxi2S710BXIw5jRUYlzY8Wfa_Q", org="Universidad de Mondragon")
write_api = client.write_api(bucket = "sensor_data", record =point)

def guardar_en_influxdb(data, prediccion):
    """
    Guarda los datos y las predicciones en InfluxDB.
    """
    try:
        point = Point("predicciones") \
            .field("sensor_1", data.get("sensor_1", 0)) \
            .field("sensor_2", data.get("sensor_2", 0)) \
            .field("prediccion", prediccion[0]) \
            .time(data.get("timestamp", int(time.time() * 1e9)))  # Timestamp en nanosegundos
        write_api.write(bucket=bucket, record=point)
        print(f"Guardado en InfluxDB: {data} | Predicción: {prediccion[0]}")
    except Exception as e:
        print(f"Error al guardar en InfluxDB: {e}")

# Cargar el modelo entrenado desde un archivo pickle
model_filename = 'rf_model_sin3sensores_sinbajaimportancia.pkl'
with open(model_filename, 'rb') as file:
    modelo = pickle.load(file)

# Obtener las columnas que el modelo espera
expected_features = modelo.feature_names_in_

# Configurar el consumer de Kafka
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'prediction_group',
    'auto.offset.reset': 'earliest'
})

# Suscribirse al tópico
consumer.subscribe(['sensor_data_1'])

print("Esperando mensajes...")



def fix_json_format(broken_json):
    """
    Intenta corregir un JSON malformado reemplazando comillas simples por dobles
    y limpiando ciertos caracteres que pueden causar errores.
    """
    # Reemplazar comillas simples por dobles
    replaced = broken_json.replace("'", '"')
    replaced = replaced.strip()
    # Eliminar posibles comas sobrantes antes de llaves/corchetes de cierre
    replaced = re.sub(r",\s*}", "}", replaced)
    replaced = re.sub(r",\s*\]", "]", replaced)
    return json.loads(replaced)

try:
    while True:
        msg = consumer.poll(1.0)  # Espera un segundo por mensajes

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # Fin de la partición
                continue
            else:
                print(f"Error en el consumer: {msg.error()}")
                break

        # Procesar el mensaje recibido
        try:
            raw_message = msg.value().decode('utf-8')
            try:
                # Primer intento de parsear JSON
                row_json = json.loads(raw_message)
            except json.JSONDecodeError:
                # Si falla, intentamos “corregir” el formato
                print("Error en el formato JSON. Intentando corregir...")
                row_json = fix_json_format(raw_message)

            # Verificar si el JSON es un dict (una sola fila) o una lista de dicts
            if isinstance(row_json, dict):
                # Crear DataFrame de una sola fila
                row_df = pd.DataFrame([row_json])
            elif isinstance(row_json, list):
                # Si es lista de diccionarios, creamos DataFrame
                # (si la lista es de escalares, esto también dará error)
                row_df = pd.DataFrame(row_json)
            else:
                raise ValueError(
                    "El mensaje JSON no es ni un diccionario ni una lista de diccionarios."
                )

            # Eliminar la columna 'Etiqueta' si existe
            if 'Etiqueta' in row_df.columns:
                row_df.drop(columns=['Etiqueta'], inplace=True)

            # Ajustar las columnas al orden esperado por el modelo
            # (solo las que existan; si faltan columnas, también podría fallar)
            row_df = row_df[[col for col in expected_features if col in row_df.columns]]

            # Realizar la predicción
            prediccion = modelo.predict(row_df)
            print(f"Predicción: {prediccion}")

            guardar_en_influxdb(row_df.iloc[0], prediccion)

        except Exception as e:
            print(f"Error procesando el mensaje: {e}")

except KeyboardInterrupt:
    print("Interrupción por teclado, cerrando...")

finally:
    consumer.close()
    client.close()