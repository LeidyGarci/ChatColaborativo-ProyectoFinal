"""
config.py — Configuración del servidor de chat

Contiene parámetros para la conexión, almacenamiento y codificación.
Se utiliza tanto en el núcleo del servidor como en los módulos relacionados.
"""

# Dirección IP del servidor (usar la IP local de tu equipo)
SERVIDOR_HOST = "192.168.1.70"

# Puerto TCP donde escuchará el servidor
SERVIDOR_PUERTO = 5000

# Ruta del archivo JSON donde se almacenará el historial de mensajes
ARCHIVO_HISTORIAL = "../datos/historial.json"

# Tamaño máximo de buffer para recibir mensajes (bytes)
BUFFER = 1024

# Codificación de caracteres utilizada para enviar y recibir datos
CODIFICACION = "utf-8"
