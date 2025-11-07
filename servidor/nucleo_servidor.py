"""
=============================================================
Descripción general:
Este módulo implementa el núcleo del sistema servidor del
proyecto Chat Colaborativo con Salas Temáticas. Permite la
comunicación en tiempo real entre múltiples clientes
utilizando sockets TCP y manejo de hilos (threading).

Responsabilidades principales:
- Escuchar y aceptar conexiones entrantes.
- Gestionar usuarios y salas de chat.
- Recibir y retransmitir mensajes.
- Registrar historiales en formato JSON.
- Validar nombres únicos por conexión.
=============================================================
"""

import socket
import threading
import json
import os

# ============================================================
# CLASE SalaChat
# ------------------------------------------------------------
# Representa una sala de chat donde se agrupan usuarios.
# Gestiona la entrada, salida y distribución de mensajes.
# ============================================================
class SalaChat:
    def __init__(self, nombre):
        self.nombre = nombre
        self.usuarios = []  # Lista de objetos UsuarioServidor

    def agregar_usuario(self, usuario):
        """Agrega un nuevo usuario a la sala."""
        self.usuarios.append(usuario)
        self.notificar_entrada(usuario.nombre)

    def eliminar_usuario(self, usuario):
        """Elimina un usuario y notifica su salida."""
        if usuario in self.usuarios:
            self.usuarios.remove(usuario)
            self.notificar_salida(usuario.nombre)

    def notificar_entrada(self, nombre_usuario):
        """Envía mensaje a todos los usuarios al entrar alguien nuevo."""
        mensaje = f"[{self.nombre}] ➤ {nombre_usuario} se ha unido a la sala."
        self.broadcast(mensaje)

    def notificar_salida(self, nombre_usuario):
        """Envía mensaje a todos los usuarios cuando alguien sale."""
        mensaje = f"[{self.nombre}] ➤ {nombre_usuario} ha salido de la sala."
        self.broadcast(mensaje)

    def broadcast(self, mensaje):
        """Reenvía un mensaje a todos los usuarios de la sala."""
        for usuario in self.usuarios:
            try:
                usuario.conexion.sendall(mensaje.encode('utf-8'))
            except:
                pass  # Si un usuario desconectó abruptamente, se ignora el error


# ============================================================
# CLASE UsuarioServidor (hereda de threading.Thread)
# ------------------------------------------------------------
# Representa la atención individual de un cliente conectado.
# Cada instancia corre en un hilo independiente.
# ============================================================
class UsuarioServidor(threading.Thread):
    def __init__(self, conexion, direccion, servidor):
        super().__init__()
        self.conexion = conexion
        self.direccion = direccion
        self.servidor = servidor
        self.nombre = None
        self.sala = None
        self.activo = True

    def run(self):
        """Método principal que se ejecuta al iniciar el hilo."""
        try:
            # Paso 1: Solicitar nombre del usuario
            self.conexion.sendall("BIENVENIDO#Ingrese su nombre:".encode('utf-8'))
            nombre = self.conexion.recv(1024).decode('utf-8').strip()

            # Validación de nombre único
            if not self.servidor.nombre_disponible(nombre):
                self.conexion.sendall("ERROR#Nombre ya en uso.".encode('utf-8'))
                self.conexion.close()
                return

            self.nombre = nombre
            self.servidor.usuarios[self.nombre] = self
            self.conexion.sendall("OK#Conexión establecida con el servidor.".encode('utf-8'))
            print(f"[+] Usuario conectado: {self.nombre} desde {self.direccion}")

            # Paso 2: Ciclo principal de escucha
            while self.activo:
                data = self.conexion.recv(1024).decode('utf-8')
                if not data:
                    break
                self.procesar_comando(data.strip())
        except:
            pass
        finally:
            self.desconectar()

    # --------------------------------------------------------
    # Procesamiento de comandos según el protocolo
    # --------------------------------------------------------
    def procesar_comando(self, mensaje):
        """
        Procesa los comandos enviados por el cliente.
        Formato esperado: COMANDO#PARAMETROS
        Ejemplo: JOIN_SALA#General
        """
        if "#" in mensaje:
            comando, *parametros = mensaje.split("#")
        else:
            comando = mensaje
            parametros = []

        if comando == "JOIN_SALA":
            nombre_sala = parametros[0] if parametros else "General"
            self.servidor.unir_a_sala(self, nombre_sala)

        elif comando == "MSG":
            if self.sala:
                texto = parametros[0] if parametros else ""
                mensaje_final = f"{self.nombre}: {texto}"
                self.sala.broadcast(mensaje_final)
                self.servidor.guardar_mensaje(self.sala.nombre, self.nombre, texto)

        elif comando == "SALIR":
            self.activo = False

    # --------------------------------------------------------
    def desconectar(self):
        """Cierra la conexión del cliente y limpia la sesión."""
        if self.sala:
            self.sala.eliminar_usuario(self)
        if self.nombre in self.servidor.usuarios:
            del self.servidor.usuarios[self.nombre]
        self.conexion.close()
        print(f"[-] Usuario desconectado: {self.nombre}")


# ============================================================
# CLASE ServidorPrincipal
# ------------------------------------------------------------
# Controla todas las conexiones entrantes y las salas activas.
# ============================================================
class ServidorPrincipal:
    def __init__(self, host='127.0.0.1', puerto=5000):
        self.host = host
        self.puerto = puerto
        self.usuarios = {}  # {nombre: UsuarioServidor}
        self.salas = {}     # {nombre_sala: SalaChat}
        self.archivo_historial = os.path.join("datos", "historial.json")
        self.cargar_historial()

    # --------------------------------------------------------
    def iniciar(self):
        """Inicia el servidor y acepta conexiones."""
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor_socket.bind((self.host, self.puerto))
        servidor_socket.listen()
        print(f"[SERVIDOR] En ejecución en {self.host}:{self.puerto}")

        try:
            while True:
                conexion, direccion = servidor_socket.accept()
                usuario = UsuarioServidor(conexion, direccion, self)
                usuario.start()
        except KeyboardInterrupt:
            print("\n[SERVIDOR] Finalizado manualmente.")
        finally:
            servidor_socket.close()

    # --------------------------------------------------------
    def unir_a_sala(self, usuario, nombre_sala):
        """Agrega un usuario a una sala existente o nueva."""
        if nombre_sala not in self.salas:
            self.salas[nombre_sala] = SalaChat(nombre_sala)
        sala = self.salas[nombre_sala]
        usuario.sala = sala
        sala.agregar_usuario(usuario)
        usuario.conexion.sendall(f"OK#Unido a la sala {nombre_sala}".encode('utf-8'))

    # --------------------------------------------------------
    def guardar_mensaje(self, sala, usuario, texto):
        """Guarda los mensajes en un archivo JSON."""
        mensaje = {"sala": sala, "usuario": usuario, "texto": texto}
        try:
            with open(self.archivo_historial, "a", encoding="utf-8") as f:
                f.write(json.dumps(mensaje, ensure_ascii=False) + "\n")
        except:
            print("[ERROR] No se pudo registrar el mensaje.")

    # --------------------------------------------------------
    def cargar_historial(self):
        """Crea el archivo de historial si no existe."""
        if not os.path.exists("datos"):
            os.makedirs("datos")
        if not os.path.exists(self.archivo_historial):
            with open(self.archivo_historial, "w", encoding="utf-8") as f:
                f.write("")

    # --------------------------------------------------------
    def nombre_disponible(self, nombre):
        """Verifica si el nombre de usuario no está en uso."""
        return nombre not in self.usuarios


# ============================================================
# PUNTO DE ENTRADA DIRECTO
# ------------------------------------------------------------
# Permite ejecutar este módulo directamente desde consola.
# ============================================================
if __name__ == "__main__":
    servidor = ServidorPrincipal(host='127.0.0.1', puerto=5000)
    servidor.iniciar()
