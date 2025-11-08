"""
almacenamiento.py — Gestión de historial de mensajes del servidor

Proporciona una forma de guardar y recuperar mensajes de chat en un archivo JSON.
Incluye sincronización thread-safe para permitir acceso concurrente desde múltiples hilos.
"""

import json
import os
import threading

class Almacenamiento:
    """
    Clase para manejar almacenamiento persistente de mensajes de chat.

    Atributos:
        ruta (str): Ruta del archivo JSON donde se guarda el historial.
        _lock (threading.Lock): Lock para asegurar acceso thread-safe al archivo.
    """

    def __init__(self, ruta_archivo):
        """
        Inicializa el almacenamiento, creando carpeta y archivo si no existen.

        Args:
            ruta_archivo (str): Ruta completa del archivo JSON para el historial.
        """
        self.ruta = ruta_archivo
        self._lock = threading.Lock()

        # Crear carpeta si no existe
        carpeta = os.path.dirname(self.ruta)
        if carpeta and not os.path.exists(carpeta):
            os.makedirs(carpeta)

        # Crear archivo vacío si no existe
        if not os.path.exists(self.ruta):
            with open(self.ruta, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    def guardar(self, sala, usuario, texto):
        """
        Guarda un mensaje en el historial.

        Args:
            sala (str): Nombre de la sala donde se envió el mensaje.
            usuario (str): Nombre del usuario que envió el mensaje.
            texto (str): Contenido del mensaje.
        """
        nuevo_registro = {
            "sala": sala,
            "usuario": usuario,
            "texto": texto
        }

        try:
            with self._lock:
                # Leer historial existente
                with open(self.ruta, "r", encoding="utf-8") as f:
                    historial = json.load(f)

                # Agregar nuevo mensaje
                historial.append(nuevo_registro)

                # Guardar nuevamente
                with open(self.ruta, "w", encoding="utf-8") as f:
                    json.dump(historial, f, ensure_ascii=False, indent=4)

            print(f"[HISTORIAL] Mensaje guardado de {usuario} en sala '{sala}'")

        except Exception as e:
            print(f"[ERROR AL GUARDAR HISTORIAL] {e}")

    def obtener_historial_sala(self, sala):
        """
        Recupera todos los mensajes de una sala específica.

        Args:
            sala (str): Nombre de la sala a consultar.

        Returns:
            list: Lista de diccionarios con los mensajes de la sala.
                  Cada diccionario tiene las claves: "sala", "usuario", "texto".
                  Devuelve lista vacía si ocurre un error.
        """
        try:
            with self._lock:
                with open(self.ruta, "r", encoding="utf-8") as f:
                    historial = json.load(f)
            # Filtrar mensajes de la sala solicitada
            return [msg for msg in historial if msg["sala"] == sala]
        except Exception as e:
            print(f"[ERROR AL CARGAR HISTORIAL] {e}")
            return []
