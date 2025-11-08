"""
main.py — Cliente del Chat Colaborativo UTP

Este archivo es el punto de entrada de la aplicación cliente. Se encarga de:

1. Ajustar la ruta de importación para poder acceder a los módulos del proyecto.
2. Importar la interfaz principal de la aplicación (ChatApp).
3. Ejecutar la aplicación usando el bucle principal de Tkinter.
"""

import sys
import os

# -------------------- AJUSTE DE RUTA --------------------
# Se agrega la carpeta raíz del proyecto al path para permitir
# la importación de módulos desde subcarpetas sin errores.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# -------------------- IMPORTACIÓN DE LA INTERFAZ --------------------
# Se importa la clase principal de la interfaz gráfica del chat
from interfaz import ChatApp

# -------------------- EJECUCIÓN DE LA APLICACIÓN --------------------
# Si este archivo se ejecuta directamente, se instancia y lanza la aplicación.
if __name__ == "__main__":
    app = ChatApp()      # Crear instancia de la interfaz
    app.mainloop()       # Ejecutar el bucle principal de Tkinter
