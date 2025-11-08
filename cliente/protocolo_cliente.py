"""
protocolo_cliente.py — Protocolo de comunicación del cliente con el servidor

Esta clase define métodos estáticos para interpretar las respuestas del servidor
y convertirlas en comandos y datos que pueda procesar la GUI o el backend.
Incluye además un método auxiliar para mostrar los mensajes en consola.
"""

class ProtocoloCliente:
    """
    Clase estática que define el protocolo de cliente para procesar respuestas
    del servidor y formatearlas para la GUI o la consola.
    """

    @staticmethod
    def procesar_respuesta(mensaje):
        """
        Procesa un mensaje recibido del servidor.

        - Divide el mensaje en comando y datos usando el separador '#'.
        - Si el mensaje no tiene el formato 'COMANDO#DATOS', se considera
          un mensaje de chat normal ('CHAT').

        Args:
            mensaje (str): Mensaje recibido del servidor.

        Returns:
            tuple: (comando: str, datos: str)
                - comando: nombre del comando en mayúsculas (p.ej. 'OK', 'CHAT', 'ERROR')
                - datos: contenido del mensaje
        """
        if "#" in mensaje:
            try:
                comando, datos = mensaje.split("#", 1)
            except ValueError:
                # Caso extraño pero posible: mensaje con '#' sin datos
                comando, datos = mensaje, ""
            return comando.strip().upper(), datos.strip()
        else:
            # Mensaje de chat normal, broadcast de otro usuario
            return "CHAT", mensaje

    @staticmethod
    def mostrar_respuesta(comando, datos):
        """
        Método auxiliar para mostrar en consola el mensaje recibido del servidor.
        No afecta la GUI, solo sirve para debugging o ejecución por terminal.

        Args:
            comando (str): Comando recibido.
            datos (str): Contenido del mensaje.

        Returns:
            str: Representación textual legible para consola.
        """
        if comando == "OK":
            return f"[SERVIDOR] {datos}"
        elif comando == "ERROR":
            return f"[SERVIDOR]  {datos}"
        elif comando == "USER_LIST":
            return f"[USUARIOS EN SALA] {datos}"
        elif comando == "ROOM_LIST":
            return f"[SALAS DISPONIBLES] {datos}"
        elif comando == "NOTIFY":
            return f"[NOTIFICACIÓN] {datos}"
        elif comando == "CHAT":
            return datos
        else:
            # Para comandos desconocidos
            return datos
