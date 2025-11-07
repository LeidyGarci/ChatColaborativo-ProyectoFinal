"""
=============================================================
Descripción general:
Este módulo implementa el cliente básico de consola para el
sistema Chat Colaborativo con Salas Temáticas. Permite
establecer conexión TCP con el servidor, enviar comandos y
mensajes, y recibir información en tiempo real.

Responsabilidades principales:
- Conectarse al servidor TCP.
- Enviar nombre de usuario (validado por el servidor).
- Permitir unirse a salas o crear nuevas.
- Escuchar mensajes recibidos en un hilo separado.
- Cerrar conexión al salir del chat.
=============================================================
"""

import socket
import threading

# ============================================================
# CLASE ClienteChat
# ------------------------------------------------------------
# Gestiona la conexión, envío y recepción de mensajes con el
# servidor. Implementa hilos para escuchar mensajes en paralelo.
# ============================================================
class ClienteChat:
    def __init__(self, host='127.0.0.1', puerto=5000):
        self.host = host
        self.puerto = puerto
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.activo = True

    # --------------------------------------------------------
    def conectar(self):
        """Inicia la conexión con el servidor y establece el flujo de comunicación."""
        try:
            self.socket_cliente.connect((self.host, self.puerto))
            print(f"[CLIENTE] Conectado al servidor en {self.host}:{self.puerto}")

            # Paso 1: recibir mensaje de bienvenida del servidor
            mensaje_inicial = self.socket_cliente.recv(1024).decode('utf-8')
            print(mensaje_inicial)

            # Paso 2: ingresar nombre de usuario
            nombre = input("Tu nombre: ").strip()
            self.socket_cliente.sendall(nombre.encode('utf-8'))

            # Paso 3: recibir confirmación del servidor
            respuesta = self.socket_cliente.recv(1024).decode('utf-8')
            if respuesta.startswith("ERROR"):
                print("[SERVIDOR]:", respuesta)
                self.activo = False
                return

            print("[SERVIDOR]:", respuesta)

            # Paso 4: iniciar hilo receptor (ahora que ya se estableció conexión)
            hilo_receptor = threading.Thread(target=self.recibir_mensajes)
            hilo_receptor.daemon = True
            hilo_receptor.start()

            # Paso 5: abrir el menú principal del chat
            self.menu_principal()

        except ConnectionRefusedError:
            print("[ERROR] No se pudo conectar al servidor. Verifica que esté activo.")
        except Exception as e:
            print(f"[ERROR] Error de conexión: {e}")

    # --------------------------------------------------------
    def menu_principal(self):
        """Muestra las opciones disponibles y permite enviar comandos."""
        print("\n--- MENÚ PRINCIPAL ---")
        print("Comandos disponibles:")
        print("1. JOIN_SALA#<nombre_sala>  → Unirse o crear una sala de chat")
        print("2. MSG#<texto>              → Enviar mensaje en la sala actual")
        print("3. SALIR                    → Desconectarse del servidor\n")

        while self.activo:
            try:
                comando = input(">> ").strip()
                if comando.lower() == "salir":
                    self.enviar("SALIR")
                    self.activo = False
                    break
                elif comando:
                    self.enviar(comando)
            except KeyboardInterrupt:
                self.enviar("SALIR")
                break

        print("[CLIENTE] Desconectado.")
        self.cerrar()

    # --------------------------------------------------------
    def enviar(self, mensaje):
        """Envía un comando o texto al servidor."""
        try:
            self.socket_cliente.sendall(mensaje.encode('utf-8'))
        except:
            print("[ERROR] No se pudo enviar el mensaje.")
            self.activo = False

    # --------------------------------------------------------
    def recibir_mensajes(self):
        """Escucha constantemente los mensajes enviados por el servidor."""
        while self.activo:
            try:
                data = self.socket_cliente.recv(1024).decode('utf-8')
                if not data:
                    break
                print("\n" + data + "\n>> ", end="")
            except:
                break
        print("[SERVIDOR] Conexión finalizada.")

    # --------------------------------------------------------
    def cerrar(self):
        """Cierra la conexión del cliente."""
        try:
            self.socket_cliente.close()
        except:
            pass


# ============================================================
# PUNTO DE ENTRADA DIRECTO
# ------------------------------------------------------------
# Permite ejecutar el cliente directamente desde consola.
# ============================================================
if __name__ == "__main__":
    cliente = ClienteChat(host='127.0.0.1', puerto=5000)
    cliente.conectar()
