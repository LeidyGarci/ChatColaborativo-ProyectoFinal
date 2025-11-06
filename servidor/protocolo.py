# protocolo.py
"""
Módulo de protocolo de comunicación
-----------------------------------
Define cómo estructurar e interpretar los mensajes entre cliente y servidor.
"""

class Protocolo:
    def construir_comando(self, comando, *parametros):
        """
        Construye un mensaje con formato: #COMANDO#param1#param2#...#
        """
        return '#' + '#'.join([comando] + list(parametros)) + '#'

    def interpretar_mensaje(self, mensaje):
        """
        Interpreta un mensaje y devuelve un diccionario con comando y parámetros.
        """
        partes = mensaje.strip('#').split('#')
        if len(partes) == 0:
            return None
        return {
            'comando': partes[0],
            'parametros': partes[1:]
        }

    def validar_formato(self, mensaje):
        """
        Valida que el mensaje tenga al menos un comando
        """
        return mensaje.startswith('#') and mensaje.endswith('#')
