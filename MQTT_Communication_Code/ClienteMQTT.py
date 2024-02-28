import paho.mqtt.client as mqtt
import psutil
import platform
from datetime import datetime
import uuid
import json
import time


# Configuración del broker MQTT
broker_address = "broker.hivemq.com"
port = 1883
topic = "grupo4"

# Función que se ejecuta cuando se conecta al broker
def on_connect(client, userdata, flags, rc):
    print(f"Conectado con código de resultado {rc}")
    client.subscribe(topic)

# Función para obtener el rendimiento del CPU
def obtener_rendimiento_cpu():
    return psutil.cpu_percent(interval=1)

# Función para obtener el rendimiento de la memoria
def obtener_rendimiento_memoria():
    return psutil.virtual_memory().percent

# Función para obtener el rendimiento de la red
def obtener_rendimiento_red():
    return psutil.net_io_counters().bytes_recv / 1024**3

# Función para obtener el sistema operativo
def obtener_sistema_operativo():
    return platform.system()

def on_message(client, userdata, msg):
    print(f"\nMensaje recibido:\n {msg.payload.decode()}")


# Configuración del cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Conexión al broker
client.connect(broker_address, port, 60)
client.loop_start()

try:
    while True:
        # Recolecta datos de rendimiento
        rendimiento_cpu = obtener_rendimiento_cpu()
        rendimiento_memoria = obtener_rendimiento_memoria()
        rendimiento_red = obtener_rendimiento_red()
        sistema_operativo = obtener_sistema_operativo()

        # Obtén la fecha y hora actual
        fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Obtén la dirección MAC
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(5, -1, -1)])

        # Construye un diccionario con los datos
        datos = {
            "fecha_hora": fecha_hora_actual,
            "mac_address": mac_address,
            "rendimiento_cpu": rendimiento_cpu,
            "rendimiento_memoria": rendimiento_memoria,
            "rendimiento_red": rendimiento_red,
            "sistema_operativo": sistema_operativo
        }

        # Convierte el diccionario a una cadena JSON
        mensaje_json = json.dumps(datos, indent=2)  # Usa indent para formatear la salida JSON

        # Envia el mensaje JSON al broker MQTT
        client.publish(topic, mensaje_json)

        # Imprime cada línea del mensaje
        print("Mensaje JSON enviado:")
        for linea in mensaje_json.split('\n'):
            print(linea)

        # Espera 10 segundos antes de enviar el siguiente mensaje
        time.sleep(10)



except KeyboardInterrupt:
    # Desconectar al recibir una interrupción del teclado (Ctrl+C)
    client.disconnect()
    client.loop_stop()
