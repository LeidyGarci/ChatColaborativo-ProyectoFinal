"""
config.py — Configuración del cliente de chat

Este archivo define los parámetros de conexión y comportamiento del cliente
del sistema de chat colaborativo. Contiene la información necesaria para
conectarse al servidor, manejar la codificación de mensajes y mostrar
mensajes iniciales de bienvenida al usuario.

Constantes definidas:
- HOST: Dirección IP del servidor al que se conectará el cliente.
- PORT: Puerto TCP del servidor.
- BUFFER: Tamaño en bytes del buffer de recepción de mensajes.
- CODIFICACION: Codificación de texto utilizada para enviar y recibir datos.
- MENSAJE_BIENVENIDA: Mensaje informativo mostrado al usuario al conectarse,
  indicando los comandos principales que puede usar.
"""

# Dirección IP del servidor al que se conectará el cliente
HOST = "192.168.1.70"

# Puerto TCP del servidor
PORT = 5000

# Tamaño del buffer de recepción en bytes
BUFFER = 1024

# Codificación utilizada para enviar y recibir mensajes (UTF-8)
CODIFICACION = "utf-8"

# Mensaje de bienvenida que se muestra al usuario al iniciar sesión
# Describe los comandos principales disponibles en la sesión de chat
MENSAJE_BIENVENIDA = (
    "[CLIENTE] Conectado al servidor.\n"
    "Use los siguientes comandos:\n"
    "  JOIN_SALA#<nombre> → Unirse o crear una sala.\n"
    "  MSG#<texto>        → Enviar mensaje a la sala actual.\n"
    "  SALIR              → Cerrar la sesión.\n"
)

# Mensaje de despedida al desconectarse del servidor
MENSAJE_DESPEDIDA = "[CLIENTE] Desconectado del servidor."