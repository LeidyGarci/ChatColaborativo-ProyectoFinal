# almacenamiento.py
"""
Módulo de almacenamiento de mensajes del chat
---------------------------------------------
Permite guardar mensajes de cada sala en un archivo JSON y leerlos.
"""

import json
import os

class Almacenamiento:
    def __init__(self, ruta_archivo='datos/historial.json'):
        self.ruta_archivo = ruta_archivo
        self.inicializar_archivo()

    def inicializar_archivo(self):
        """Crea el archivo JSON si no existe"""
        if not os.path.exists(self.ruta_archivo):
            with open(self.ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump({}, f)  # Diccionario vacío para salas

    def guardar_mensaje(self, sala, usuario, mensaje):
        """Guarda un mensaje en la sala correspondiente"""
        with open(self.ruta_archivo, 'r+', encoding='utf-8') as f:
            datos = json.load(f)
            if sala not in datos:
                datos[sala] = []
            datos[sala].append({'usuario': usuario, 'mensaje': mensaje})
            f.seek(0)
            json.dump(datos, f, indent=4, ensure_ascii=False)
            f.truncate()

    def cargar_historial(self, sala):
        """Devuelve la lista de mensajes de una sala"""
        with open(self.ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        return datos.get(sala, [])
