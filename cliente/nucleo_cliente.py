import socket
import threading
from cliente.protocolo_cliente import ProtocoloCliente


class ClienteChat:
    """
    Clase principal que maneja la comunicación del cliente con el servidor TCP.
    Sigue el protocolo de comandos delimitado por #.
    """

    def __init__(self, host="127.0.0.1", puerto=5000, callback_mensaje=None):
        """
        Inicializa el socket del cliente y las variables básicas.
        - host: dirección del servidor
        - puerto: puerto TCP
        - callback_mensaje: función que se ejecuta cuando llega un mensaje del servidor
        """
        self.host = host
        self.puerto = puerto
        self.socket_cliente = None
        self.nombre_usuario = None
        self.sala_actual = None
        self.escuchando = False
        self.hilo_escucha = None
        self.protocolo = ProtocoloCliente()
        self.callback_mensaje = callback_mensaje  # para comunicar con Tkinter


    #Conexión y autenticación
    
    def conectar(self, nombre_usuario: str):
        #Establece conexión con el servidor e inicia el hilo de escucha.
        self.nombre_usuario = nombre_usuario
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_cliente.connect((self.host, self.puerto))
        self.escuchando = True

        #Enviar comando de conexión al servidor
        comando = self.protocolo.construir_comando("CONECTAR", self.nombre_usuario)
        self.enviar_comando(comando)

        #Inicia el hilo para escuchar mensajes del servidor
        self.hilo_escucha = threading.Thread(target=self.escuchar_respuestas, daemon=True)
        self.hilo_escucha.start()
        print(f"[CLIENTE] Conectado al servidor {self.host}:{self.puerto}")


    #Envío y recepción
    def enviar_comando(self, comando: str):
        #Envía un comando al servidor
        if not self.socket_cliente:
            raise ConnectionError("No hay conexión activa con el servidor.")
        self.socket_cliente.sendall(comando.encode("utf-8"))

    def escuchar_respuestas(self):
        #Escucha constantemente los mensajes del servidor.
        try:
            while self.escuchando:
                data = self.socket_cliente.recv(1024)
                if not data:
                    break

                mensaje = data.decode("utf-8").strip()
                print(f"[Servidor] {mensaje}")

                # Si la interfaz del cliente pasó un callback, notifícale
                if self.callback_mensaje:
                    self.callback_mensaje(mensaje)

        except (ConnectionResetError, OSError):
            print("Conexión cerrada por el servidor.")
        finally:
            self.desconectar()


    #Comandos específicos
    def crear_sala(self, nombre_sala: str):
        self.enviar_comando(f"#CREAR_SALA#{nombre_sala}#")

    def unir_sala(self, nombre_sala: str):
        self.sala_actual = nombre_sala
        self.enviar_comando(f"#UNIR_SALA#{nombre_sala}#")

    def enviar_mensaje(self, texto: str):
        if not self.sala_actual:
            print("[ADVERTENCIA] No estás en una sala.")
            return
        comando = f"#MENSAJE#{self.sala_actual}#{texto}#"
        self.enviar_comando(comando)

    def salir_sala(self):
        if self.sala_actual:
            self.enviar_comando(f"#SALIR_SALA#{self.sala_actual}#")
            self.sala_actual = None

    def desconectar(self):
        #Cierra la conexión
        if self.socket_cliente:
            try:
                self.enviar_comando("#DESCONECTAR#")
                self.escuchando = False
                self.socket_cliente.close()
                print("[CLIENTE] Desconectado del servidor.")
            except Exception:
                pass
            finally:
                self.socket_cliente = None