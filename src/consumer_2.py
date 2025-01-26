from confluent_kafka import Consumer, KafkaError
import pandas as pd
import pickle
import json
import re

# Cargar el modelo entrenado desde un archivo pickle
model_filename = 'rf_model_sin3sensores_sinbajaimportancia.pkl' #xgb_model_final.pkl
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
    replaced = broken_json.replace("'", '"')
    replaced = replaced.strip()
    replaced = re.sub(r",\s*}", "}", replaced)
    replaced = re.sub(r",\s*]", "]", replaced)
    return json.loads(replaced)

try:
    while True:
        msg = consumer.poll(1.0)  # Espera un segundo por mensajes

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error en el consumer: {msg.error()}")
                break

        try:
            raw_message = msg.value().decode('utf-8')
            try:
                row_json = json.loads(raw_message)
            except json.JSONDecodeError:
                print("Error en el formato JSON. Intentando corregir...")
                row_json = fix_json_format(raw_message)

            # Crear DataFrame desde el JSON recibido
            row_df = pd.DataFrame([row_json])

            # Asegurar que todas las columnas esperadas estén presentes
            for col in expected_features:
                if col not in row_df.columns:
                    row_df[col] = 0  # Rellenar con un valor por defecto

            # Ajustar el DataFrame al orden esperado por el modelo
            row_df = row_df[expected_features]

            # Realizar la predicción
            prediccion = modelo.predict(row_df)
            print(f"Predicción: {prediccion}")

        except Exception as e:
            print(f"Error procesando el mensaje: {e}")

except KeyboardInterrupt:
    print("Interrupción por teclado, cerrando...")

finally:
    consumer.close()