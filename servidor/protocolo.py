"""
protocolo.py — Definición del protocolo de comunicación del servidor

Proporciona:
- Parseo de mensajes recibidos de clientes
- Construcción de respuestas para clientes
- Validación de comandos
- Diccionario de comandos disponibles y su descripción
"""

class ProtocoloServidor:
    """
    Clase estática que define el protocolo de mensajes entre cliente y servidor.
    """

    @staticmethod
    def procesar_mensaje(mensaje):
        """
        Divide un mensaje en comando y datos.

        Formato esperado: COMANDO#DATOS
        Si no tiene '#', devuelve datos vacío.

        Args:
            mensaje (str): Mensaje recibido desde el cliente

        Returns:
            tuple: (comando, datos) donde comando está en mayúsculas y sin espacios
        """
        try:
            comando, datos = mensaje.split("#", 1)
        except ValueError:
            comando, datos = mensaje, ""
        return comando.strip().upper(), datos.strip()

    @staticmethod
    def construir_respuesta(comando, datos=""):
        """
        Construye un mensaje con formato COMANDO#DATOS.

        Args:
            comando (str): Nombre del comando
            datos (str, opcional): Datos asociados al comando. Por defecto vacío.

        Returns:
            str: Mensaje listo para enviar al cliente
        """
        return f"{comando}#{datos}"

    # Diccionario de comandos válidos y su descripción
    COMANDOS = {
        "HELLO": "Registrar usuario nuevo.",
        "JOIN_SALA": "Unirse o crear una sala.",
        "MSG": "Enviar mensaje a los usuarios de la sala actual.",
        "USER_LIST": "Solicitar la lista de usuarios en la sala.",
        "ROOM_LIST": "Solicitar la lista de salas disponibles.",
        "SALIR": "Salir del chat.",
    }

    @staticmethod
    def validar_comando(comando):
        """
        Valida si un comando recibido está permitido según COMANDOS.

        Args:
            comando (str): Comando a validar

        Returns:
            bool: True si el comando es válido, False si no lo es
        """
        return comando in ProtocoloServidor.COMANDOS.keys()
