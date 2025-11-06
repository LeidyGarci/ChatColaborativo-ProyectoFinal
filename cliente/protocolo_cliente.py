"""
Módulo de protocolo del cliente
-------------------------------
Define cómo el cliente construye e interpreta los comandos enviados al servidor.
"""

class ProtocoloCliente:
    def construir_comando(self, comando, *parametros):
        #Construye un mensaje con formato #COMANDO#param1#param2#...#
        return '#' + '#'.join([comando] + list(parametros)) + '#'

    def interpretar_mensaje(self, mensaje):
        #Devuelve un diccionario con el comando y los parámetros.
        partes = mensaje.strip('#').split('#')
        if len(partes) == 0:
            return None
        return {
            'comando': partes[0],
            'parametros': partes[1:]
        }

    def validar_formato(self, mensaje):
        #Verifica que el mensaje tenga formato válido
        return mensaje.startswith('#') and mensaje.endswith('#')