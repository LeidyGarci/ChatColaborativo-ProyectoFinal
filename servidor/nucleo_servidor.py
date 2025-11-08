"""
nucleo_servidor.py — Núcleo del servidor de chat colaborativo

Gestiona:
- Conexión de clientes
- Salas temáticas
- Envío y recepción de mensajes
- Historial de chat
- Listado de usuarios y salas

Utiliza:
- threading para manejar múltiples clientes simultáneamente
- socket para comunicación TCP
- Almacenamiento JSON para historial
- ProtocoloServidor para construcción y parseo de mensajes
"""

import socket
import threading
from protocolo import ProtocoloServidor
from almacenamiento import Almacenamiento
import config

class ServidorChat:
    """
    Clase principal del servidor de chat.

    Atributos:
        host, puerto        → Configuración de red
        servidor            → Socket principal
        clientes            → Diccionario {socket: nombre}
        salas               → Diccionario {nombre_sala: [sockets]}
        historial           → Objeto Almacenamiento para mensajes
        _lock               → Lock para operaciones thread-safe
    """

    def __init__(self):
        # Configuración del servidor TCP
        self.host = config.SERVIDOR_HOST
        self.puerto = config.SERVIDOR_PUERTO
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.servidor.bind((self.host, self.puerto))
        self.servidor.listen()

        print(f"[SERVIDOR] En ejecución en {self.host}:{self.puerto}")
        print("[SERVIDOR] Esperando conexiones...")

        # Estructuras de datos
        self.clientes = {}       # {socket: nombre}
        self.salas = {}          # {nombre_sala: [sockets]}
        for s in ("Juegos", "Series"):  # Salas por defecto
            self.salas[s] = []

        self.historial = Almacenamiento(config.ARCHIVO_HISTORIAL)
        self._lock = threading.Lock()

    def iniciar(self):
        """Acepta conexiones entrantes y lanza un hilo por cliente."""
        try:
            while True:
                cliente, direccion = self.servidor.accept()
                hilo = threading.Thread(target=self.manejar_cliente,
                                        args=(cliente, direccion), daemon=True)
                hilo.start()
        except KeyboardInterrupt:
            print("[SERVIDOR] Cerrando servidor...")
            self.servidor.close()

    def manejar_cliente(self, cliente, direccion):
        """
        Bucle principal de manejo de cliente:
        - Recepción de mensajes
        - Procesamiento según protocolo
        - Gestión de salas y desconexión
        """
        print(f"[NUEVA CONEXIÓN] Desde {direccion}")
        nombre = None
        sala_actual = None

        try:
            while True:
                mensaje = cliente.recv(config.BUFFER).decode(config.CODIFICACION)
                if not mensaje:
                    break

                comando, datos = ProtocoloServidor.procesar_mensaje(mensaje)

                # ------------------ COMANDOS ------------------
                if comando == "HELLO":
                    # Registro de nombre de usuario
                    nombre = datos
                    if self.nombre_duplicado(nombre):
                        cliente.send(ProtocoloServidor.construir_respuesta(
                            "ERROR", "Nombre ya en uso."
                        ).encode(config.CODIFICACION))
                        cliente.close()
                        return

                    with self._lock:
                        self.clientes[cliente] = nombre
                    cliente.send(ProtocoloServidor.construir_respuesta(
                        "OK", f"Conexión establecida. Bienvenido, {nombre}."
                    ).encode(config.CODIFICACION))
                    print(f"[+] Usuario conectado: {nombre}")

                elif comando == "JOIN_SALA":
                    # Usuario se une a una sala
                    sala_actual = datos
                    self.unirse_sala(cliente, sala_actual)

                    # Enviar historial previo al cliente
                    historial_sala = self.historial.obtener_historial_sala(sala_actual)
                    if historial_sala:
                        for msg in historial_sala:
                            try:
                                mensaje_hist = f"{msg['usuario']}: {msg['texto']}"
                                resp = ProtocoloServidor.construir_respuesta("CHAT", mensaje_hist)
                                cliente.send((resp + "\n").encode(config.CODIFICACION))
                            except Exception:
                                pass

                elif comando == "MSG" and sala_actual:
                    # Retransmitir mensaje a sala y guardar historial
                    self.retransmitir(cliente, sala_actual, datos)
                    try:
                        usuario = self.clientes.get(cliente, "Desconocido")
                        self.historial.guardar(sala_actual, usuario, datos)
                    except Exception as e:
                        print(f"[ERROR registro historial] {e}")

                elif comando == "USER_LIST":
                    self.enviar_lista_usuarios(cliente)

                elif comando == "USER_LIST_ALL":
                    # Listar todos los usuarios conectados con su sala
                    usuarios_info = []
                    with self._lock:
                        for c, nombre_usuario in self.clientes.items():
                            sala = None
                            for s, sockets in self.salas.items():
                                if c in sockets:
                                    sala = s
                                    break
                            sala_texto = sala if sala else "Sin sala"
                            usuarios_info.append(f"{nombre_usuario} ({sala_texto})")
                    texto = ", ".join(usuarios_info) if usuarios_info else "No hay usuarios conectados."
                    cliente.send(ProtocoloServidor.construir_respuesta(
                        "USER_LIST_ALL", texto
                    ).encode(config.CODIFICACION))

                elif comando == "ROOM_LIST":
                    self.enviar_lista_salas(cliente)

                elif comando == "LEAVE_SALA":
                    # Usuario abandona sala, notificar a otros
                    sala = datos
                    nombre_usuario = self.clientes.get(cliente, "Desconocido")
                    if sala in self.salas and cliente in self.salas[sala]:
                        for c in list(self.salas[sala]):
                            if c != cliente:
                                try:
                                    c.send(ProtocoloServidor.construir_respuesta(
                                        "NOTIFY", f"{nombre_usuario} ha salido de la sala {sala}."
                                    ).encode(config.CODIFICACION))
                                except Exception:
                                    self.desconectar(c, sala)
                        with self._lock:
                            if cliente in self.salas[sala]:
                                self.salas[sala].remove(cliente)
                    cliente.send(ProtocoloServidor.construir_respuesta(
                        "OK", f"Has salido de la sala {sala}."
                    ).encode(config.CODIFICACION))

                elif comando == "SALIR":
                    # Desconexión voluntaria
                    break

                else:
                    # Comando no reconocido
                    cliente.send(ProtocoloServidor.construir_respuesta(
                        "ERROR", f"Comando no reconocido: {comando}"
                    ).encode(config.CODIFICACION))

        except ConnectionResetError:
            pass
        except Exception as e:
            print(f"[ERROR hilo cliente] {e}")
        finally:
            # Limpiar cliente y sala
            self.desconectar(cliente, sala_actual)

    # ------------------ MÉTODOS AUXILIARES ------------------

    def nombre_duplicado(self, nombre):
        """Verifica si ya existe un usuario con ese nombre."""
        with self._lock:
            return nombre in self.clientes.values()

    def unirse_sala(self, cliente, sala):
        """Agrega un cliente a una sala y notifica a los demás."""
        with self._lock:
            if sala not in self.salas:
                self.salas[sala] = []
            if cliente not in self.salas[sala]:
                self.salas[sala].append(cliente)

        nombre = self.clientes.get(cliente, "Desconocido")
        print(f"[{sala}] ➤ {nombre} se ha unido.")
        self.retransmitir_evento(cliente, sala, f"{nombre} se ha unido a la sala.")
        cliente.send(ProtocoloServidor.construir_respuesta(
            "OK", f"Te has unido a la sala '{sala}'."
        ).encode(config.CODIFICACION))

    def retransmitir(self, cliente, sala, mensaje):
        """Envía un mensaje a todos los clientes de la sala."""
        nombre = self.clientes.get(cliente, "Desconocido")
        texto = f"{nombre}: {mensaje}"
        vivos = []
        for c in list(self.salas.get(sala, [])):
            try:
                c.send(f"{texto}\n".encode(config.CODIFICACION))
                vivos.append(c)
            except Exception:
                self.desconectar(c, sala)
        with self._lock:
            self.salas[sala] = vivos

    def retransmitir_evento(self, cliente, sala, mensaje):
        """Envía notificación a todos los clientes de la sala, excepto al remitente."""
        vivos = []
        for c in list(self.salas.get(sala, [])):
            try:
                if c != cliente:
                    c.send(ProtocoloServidor.construir_respuesta(
                        "NOTIFY", mensaje).encode(config.CODIFICACION))
                vivos.append(c)
            except Exception:
                self.desconectar(c, sala)
        with self._lock:
            self.salas[sala] = vivos

    def enviar_lista_usuarios(self, cliente):
        """Envía al cliente la lista de usuarios y la sala en la que están."""
        usuarios_info = []
        with self._lock:
            for c, nombre in self.clientes.items():
                sala = None
                for s, sockets in self.salas.items():
                    if c in sockets:
                        sala = s
                        break
                estado = sala if sala else "No se encuentra en una sala"
                usuarios_info.append(f"{nombre} ({estado})")
        texto = ", ".join(usuarios_info) if usuarios_info else "No hay usuarios conectados."
        cliente.send(ProtocoloServidor.construir_respuesta(
            "USER_LIST", texto
        ).encode(config.CODIFICACION))

    def enviar_lista_salas(self, cliente):
        """Envía al cliente la lista de salas existentes."""
        if not self.salas:
            cliente.send(ProtocoloServidor.construir_respuesta(
                "ROOM_LIST", "No hay salas activas."
            ).encode(config.CODIFICACION))
            return
        lista = ", ".join(self.salas.keys())
        cliente.send(ProtocoloServidor.construir_respuesta(
            "ROOM_LIST", lista
        ).encode(config.CODIFICACION))

    def desconectar(self, cliente, sala):
        """
        Elimina cliente de estructuras y notifica salida de sala.
        Cierra socket y limpia diccionarios.
        """
        nombre = self.clientes.get(cliente, "Usuario")
        print(f"[-] {nombre} se ha desconectado.")

        if sala and cliente in self.salas.get(sala, []):
            try:
                self.salas[sala].remove(cliente)
            except ValueError:
                pass
            self.retransmitir(cliente, sala, f"{nombre} ha salido de la sala.")

        with self._lock:
            if cliente in self.clientes:
                del self.clientes[cliente]

        try:
            cliente.close()
        except:
            pass

if __name__ == "__main__":
    # Inicia servidor si se ejecuta directamente
    servidor = ServidorChat()
    servidor.iniciar()
