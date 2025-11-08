"""
nucleo_cliente.py — Backend del Cliente de Chat Colaborativo UTP

Este módulo se encarga de toda la lógica de conexión, comunicación y manejo de mensajes
con el servidor, separando la lógica de la GUI. 

Proporciona:

- Conexión y desconexión del servidor.
- Envío de mensajes y comandos (join/leave room, lista de salas/usuarios).
- Recepción de mensajes en hilo separado y notificación a la GUI mediante una cola
  thread-safe (self.queue) para actualizar la interfaz sin bloquearla.
"""

import socket
import threading
import queue
import config
from protocolo_cliente import ProtocoloCliente

class BackendCliente:
    """
    Clase que maneja la conexión con el servidor y la comunicación de mensajes.

    Atributos:
        host (str): IP del servidor.
        port (int): Puerto del servidor.
        buffer (int): Tamaño del buffer para recibir datos.
        codificacion (str): Codificación de los mensajes.
        socket_cliente (socket): Socket TCP usado para comunicarse con el servidor.
        activo (bool): Estado de la conexión.
        receptor_thread (Thread): Hilo que escucha mensajes del servidor.
        queue (Queue): Cola thread-safe para enviar eventos a la GUI.
        nombre (str): Nombre del usuario conectado.
        sala_actual (str | None): Sala en la que se encuentra el usuario actualmente.
    """

    def __init__(self):
        self.host = config.HOST
        self.port = config.PORT
        self.buffer = config.BUFFER
        self.codificacion = config.CODIFICACION

        self.socket_cliente = None
        self.activo = False
        self.receptor_thread = None

        self.queue = queue.Queue()  # Cola thread-safe para comunicar eventos a la GUI

        # nombre del usuario y sala actual
        self.nombre = None
        self.sala_actual = None

    def conectar(self, nombre):
        """
        Conecta el cliente al servidor y envía el comando HELLO con el nombre del usuario.

        Args:
            nombre (str): Nombre del usuario a registrar en el servidor.

        Returns:
            tuple: (bool, str) indicando éxito y mensaje de estado.
        """
        try:
            self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_cliente.connect((self.host, self.port))
            self.activo = True
        except Exception as e:
            return False, f"No se pudo conectar: {e}"

        # Inicia el hilo que escucha mensajes del servidor
        self.receptor_thread = threading.Thread(target=self._escuchar, daemon=True)
        self.receptor_thread.start()

        self.nombre = nombre
        self._enviar_raw(f"HELLO#{nombre}")
        return True, "Conectado (esperando confirmación del servidor)"

    def _enviar_raw(self, texto):
        """
        Envía texto crudo al servidor codificado según la configuración.

        Args:
            texto (str): Mensaje o comando a enviar.
        """
        try:
            if self.activo and self.socket_cliente:
                self.socket_cliente.sendall(texto.encode(self.codificacion))
        except Exception as e:
            # Notificar error a la GUI
            self.queue.put(("ERROR", f"Error al enviar: {e}"))
            self.activo = False

    def join_room(self, nombre_sala):
        """
        Solicita unirse o crear una sala en el servidor.

        Args:
            nombre_sala (str): Nombre de la sala.
        """
        self.sala_actual = nombre_sala
        self._enviar_raw(f"JOIN_SALA#{nombre_sala}")

    def leave_room(self):
        """
        Salir de la sala actual.

        - Envía comando LEAVE_SALA al servidor.
        - Limpia la sala local.
        - Notifica a la GUI mediante la cola que se ha salido de la sala.
        """
        if self.sala_actual:
            nombre_sala = self.sala_actual
            self._enviar_raw(f"LEAVE_SALA#{nombre_sala}")  # notifica al servidor
            self.sala_actual = None
            self.queue.put(("INFO", f"Has salido de la sala {nombre_sala}"))

    def send_message(self, texto):
        """
        Envía un mensaje de chat a la sala actual.

        Args:
            texto (str): Mensaje a enviar.
        """
        if not self.sala_actual:
            self.queue.put(("ERROR", "No estás en ninguna sala."))
            return
        self._enviar_raw(f"MSG#{texto}")

    def request_rooms(self):
        """
        Solicita al servidor la lista de salas disponibles.
        """
        self._enviar_raw("ROOM_LIST#")

    def request_users(self):
        """
        Solicita al servidor la lista de todos los usuarios conectados,
        sin importar la sala en la que esté el cliente.
        """
        self._enviar_raw("USER_LIST_ALL#")

    def disconnect(self):
        """
        Desconecta el cliente del servidor.

        - Envía comando SALIR.
        - Cierra socket.
        - Actualiza estado de conexión.
        """
        try:
            if self.activo:
                self._enviar_raw("SALIR#")
            if self.socket_cliente:
                self.socket_cliente.close()
        except:
            pass
        self.activo = False

    def _escuchar(self):
        """
        Hilo que escucha continuamente mensajes del servidor.

        - Decodifica los mensajes según el protocolo.
        - Coloca eventos en la cola para que la GUI los procese.
        """
        try:
            while self.activo:
                try:
                    data = self.socket_cliente.recv(self.buffer)
                    if not data:
                        self.queue.put(("DISCONNECTED", "Conexión cerrada por el servidor."))
                        self.activo = False
                        break

                    mensaje = data.decode(self.codificacion)
                    comando, datos = ProtocoloCliente.procesar_respuesta(mensaje)
                    self.queue.put((comando, datos))
                except ConnectionResetError:
                    self.queue.put(("DISCONNECTED", "Conexión perdida."))
                    self.activo = False
                    break
                except Exception as e:
                    self.queue.put(("ERROR", f"Error recepción: {e}"))
                    self.activo = False
                    break
        finally:
            self.activo = False
