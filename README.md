# Plataforma Inteligente para Mantenimiento Predictivo

Este repositorio contiene el código, modelos y documentación para un sistema de **mantenimiento predictivo basado en inteligencia artificial**. El objetivo es maximizar la operatividad de los componentes y reducir los costos de mantenimiento en entornos industriales.

## Índice
- [Descripción General](#descripción-general)
- [Estructura del Repositorio](#estructura-del-repositorio)
- [Requisitos](#requisitos)
- [Instrucciones de Uso](#instrucciones-de-uso)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Modelos y Técnicas](#modelos-y-técnicas)
- [Resultados](#resultados)
- [Líneas Futuras y Mejoras](#líneas-futuras-y-mejoras)
- [Autores](#autores)

## Descripción General

Este proyecto aborda dos problemas principales:
1. **Detección temprana de fallos en rodamientos** usando análisis de series temporales y machine learning.
2. **Detección y localización de defectos en piezas** mediante segmentación de imágenes usando deep learning.

Los datos provienen de sensores industriales y un conjunto de imágenes etiquetadas con mapas de bits que identifican defectos.

## Estructura del Repositorio

- **`Analisis y preproceso.ipynb`**: Análisis inicial de datos, generación de etiquetas y preprocesamiento para los modelos de fallos en rodamientos.
- **`Modelos y entrenamiento.ipynb`**: Entrenamiento de modelos de machine learning para la clasificación de fallos.
- **`Data_augmentation.ipynb`**: Generación de imágenes sintéticas para balancear el conjunto de datos.
- **`Model_trainer_segmentation.ipynb`**: Entrenamiento de modelos de segmentación para detectar defectos en piezas.
- **`Model_tester_segmentation.ipynb`**: Evaluación de los modelos de segmentación.
- **`Model_trainer_with_classification.ipynb`**: Entrenamiento de un modelo híbrido para clasificación y segmentación simultánea.
- **`Model_tester_hibrid.ipynb`**: Evaluación del modelo híbrido.
- **`producer_1_v1.py`**: Productor Kafka que envía datos de sensores simulados a un tópico.
- **`consumer_1.py`**: Consumidor Kafka que recibe datos, realiza predicciones y las guarda en InfluxDB.

## Requisitos

### Hardware
- GPU compatible con CUDA (para entrenar modelos de segmentación).

### Software
- Python 3.8+
- Librerías principales: `pandas`, `numpy`, `scikit-learn`, `torch`, `torchvision`, `confluent-kafka`, `influxdb-client`, etc.

Instala todas las dependencias ejecutando:
```bash
pip install -r requirements.txt
```

### Configuración
- Configura tu instancia de Kafka y crea los tópicos necesarios (`sensor_data_1`).
- Configura tu base de datos en InfluxDB para almacenar predicciones y datos de sensores.

## Instrucciones de Uso

### 1. Configuración Inicial
1. **Instalación de Dependencias**:
   Asegúrate de tener Python 3.8 o superior instalado en tu sistema. Instala las dependencias necesarias ejecutando:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuración de Kafka**:
   - Inicia un servidor Kafka local o remoto.
   - Crea un tópico llamado `sensor_data_1` para el envío y recepción de datos.

3. **Configuración de InfluxDB**:
   - Asegúrate de tener InfluxDB instalado y en ejecución.
   - Crea un bucket llamado `sensor_data`.
   - Modifica los tokens y configuraciones en `consumer_1.py` según tus credenciales de InfluxDB.

### 2. Ingesta de Datos con Kafka

#### Productor:
El productor lee un archivo CSV con datos de sensores y los envía al tópico de Kafka.
1. Asegúrate de tener el archivo de datos `Data_final.csv` en el directorio raíz del proyecto.
2. Ejecuta el siguiente comando para iniciar el productor:
   ```bash
   python producer_1_v1.py
   ```
   El productor enviará un mensaje cada 3 segundos al tópico configurado.
3. Ejecución con la base de datos original, por tanto, es método para prescindir de cualquier preprocesado:
- Ingesta automáticamente de todas las carpetas, cálculo de estadísticos para cada régimen de fallo.
- Envío por mensaje a través de flask: 'sensor_data_1'
     ```bash
   python producer_1_v1.py
   ```

#### Consumidor:
El consumidor recibe los datos del tópico de Kafka, realiza predicciones y almacena los resultados en InfluxDB.
1. Ejecuta el siguiente comando para iniciar el consumidor:
   ```bash
   python consumer_1.py
   ```
   Verás en la consola las predicciones realizadas y mensajes como:
   ```
   Predicción: [1]
   Guardado en InfluxDB: {"sensor_1": 0.23, "sensor_2": 0.45} | Predicción: 1
   ```
- Tambi
### 3. Entrenamiento de Modelos

#### Clasificación de Fallos en Rodamientos:
1. Abre el notebook `Modelos y entrenamiento.ipynb`.
2. Ejecuta las celdas en orden para:
   - Preprocesar los datos.
   - Entrenar modelos de Random Forest, XGBoost y Gradient Boosting.
   - Evaluar las métricas de cada modelo.

#### Segmentación de Imágenes:
1. Abre el notebook `Model_trainer_segmentation.ipynb`.
2. Configura los hiperparámetros según tus necesidades.
3. Ejecuta las celdas para entrenar el modelo U-Net.

#### Modelo Híbrido:
1. Usa el notebook `Model_trainer_with_classification.ipynb` para el entrenamiento.
2. Evalúa el modelo con `Model_tester_hibrid.ipynb` para obtener métricas tanto de clasificación como de segmentación.

### 4. Visualización de Resultados

Los resultados de las predicciones se almacenan en InfluxDB y pueden visualizarse con Grafana:
1. Conecta Grafana a tu base de datos InfluxDB.
2. Crea un dashboard personalizado para mostrar:
   - Gráficos de las predicciones realizadas.
   - Alertas en tiempo real sobre fallos detectados.

## Ejemplos de Uso

### 1. **Envío de Datos de Sensores**
Para enviar datos desde un archivo CSV al tópico de Kafka:
```bash
python producer_1_v1.py
```
### 2. **Consumo de Datos y Predicción**
Para consumir datos del tópico y realizar predicciones:
```bash
python consumer_1.py
```

### 3. **Entrenamiento y Evaluación**
Abre los notebooks y ejecuta las celdas para entrenar y evaluar los modelos.

## Modelos y Técnicas

1. **Clasificación de Fallos en Rodamientos**:
   - Modelos: Random Forest, XGBoost, Gradient Boosting.
   - Métricas: Accuracy, Precision, Recall, F1-Score.

2. **Segmentación de Imágenes**:
   - Modelo: U-Net.
   - Métricas: IoU, Dice.

3. **Modelo Híbrido**:
   - Predicción combinada de clasificación binaria y segmentación semántica.

## Resultados

- **Rodamientos**: El modelo Random Forest logra una precisión del 93%, siendo el mejor clasificador de fallos.
- **Segmentación**: El modelo U-Net obtiene un IoU del 70% y un coeficiente Dice del 75%.
- **Híbrido**: Precisión combinada cercana al 90%, con resultados robustos en ambas tareas.

## Líneas Futuras y Mejoras

### Ampliación del Conjunto de Datos
- Recopilar muestras reales de rodamientos defectuosos en escenarios industriales reales.
- Aumentar la diversidad en el conjunto de datos, incluyendo fallos combinados y condiciones variables (velocidad, carga, etc.).

### Mejora de Modelos
- Implementar arquitecturas más avanzadas como DeepLab o Segment Anything Model (SAM) para mejorar la segmentación.
- Optimizar el modelo híbrido utilizando arquitecturas más ligeras como MobileNet o EfficientNet para reducir el costo computacional.

### Escalabilidad y Robustez
- Validar el sistema en entornos industriales reales para garantizar su robustez frente a condiciones adversas.
- Escalar la plataforma para manejar grandes volúmenes de datos en tiempo real.

### Funcionalidades Adicionales
- Desarrollar una clasificación multicategoría para distinguir entre diferentes tipos de defectos.
- Integrar el sistema con líneas de producción automatizadas para proporcionar retroalimentación en tiempo real.

### Visualización y Reportes
- Mejorar los dashboards en Grafana para incluir gráficos avanzados de métricas y análisis de predicciones.
- Generar reportes automáticos de desempeño del sistema en formato PDF.

### Optimización Computacional
- Implementar técnicas de cuantización de modelos para reducir el uso de memoria en dispositivos edge.
- Experimentar con frameworks optimizados para inferencia como TensorRT.

### Despliegue
- Preparar la plataforma para su despliegue en la nube (AWS, GCP, Azure) o en dispositivos edge para producción en tiempo real.

## Autores

- Carlos Cabrera
- Jerai Tovar
- Nagore Portilla

**Fecha del Proyecto**: Enero de 2025

