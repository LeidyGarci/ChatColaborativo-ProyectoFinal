import socket
import threading
from almacenamiento import Almacenamiento  # Maneja el historial de mensajes
from protocolo import Protocolo  # Procesa los comandos de cliente

# ===========================
# Clase Hilo que representa a cada cliente conectado
# ===========================
class ClienteHilo(threading.Thread):
    def __init__(self, conexion, direccion, servidor):
        super().__init__()
        self.conexion = conexion          # Socket del cliente
        self.direccion = direccion        # Dirección IP y puerto del cliente
        self.servidor = servidor          # Referencia al ServidorPrincipal
        self.nombre = None                # Nombre único del cliente
        self.sala_actual = None           # Sala donde está conectado

    # Método que se ejecuta al iniciar el hilo
    def run(self):
        try:
            while True:
                data = self.conexion.recv(1024).decode('utf-8')
                if not data:  # Cliente cerró la conexión de manera normal
                    break
                print(f"[RECIBIDO] {data} de {self.direccion}")
                # Aquí se procesarían los comandos usando el Protocolo
                # Ejemplo: self.procesar_comando(data)
        except ConnectionResetError:
            print(f"[DESCONECTADO (error)] {self.direccion}")  # Desconexión inesperada
        finally:
            self.conexion.close()
            print(f"[DESCONECTADO] {self.direccion}")
            if self.nombre:
                self.servidor.eliminar_cliente(self.nombre)  # Limpieza en el servidor

# ===========================
# Servidor Principal
# ===========================
class ServidorPrincipal:
    def __init__(self, host='127.0.0.1', puerto=5000):
        self.host = host
        self.puerto = puerto
        self.clientes = {}  # Diccionario {nombre_cliente: ClienteHilo}
        self.salas = {}     # Diccionario {nombre_sala: SalaChat}
        self.almacenamiento = Almacenamiento()  # Para guardar historial
        self.protocolo = Protocolo()            # Para procesar comandos
        self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Inicia el servidor y queda a la espera de conexiones
    def iniciar_servidor(self):
        self.servidor_socket.bind((self.host, self.puerto))
        self.servidor_socket.listen(5)
        print(f"[INICIADO] Servidor escuchando en {self.host}:{self.puerto}")

        while True:
            conexion, direccion = self.servidor_socket.accept()
            print(f"[NUEVA CONEXIÓN] {direccion}")
            cliente_hilo = ClienteHilo(conexion, direccion, self)
            cliente_hilo.start()

    # Registra un cliente con nombre único
    def registrar_cliente(self, nombre, cliente_hilo):
        self.clientes[nombre] = cliente_hilo
        print(f"[CLIENTE REGISTRADO] {nombre}")

    # Elimina un cliente del servidor
    def eliminar_cliente(self, nombre):
        if nombre in self.clientes:
            del self.clientes[nombre]
            print(f"[CLIENTE ELIMINADO] {nombre}")

# ===========================
# Permite ejecutar el servidor directamente
# ===========================
if __name__ == "__main__":
    servidor = ServidorPrincipal()
    servidor.iniciar_servidor()
