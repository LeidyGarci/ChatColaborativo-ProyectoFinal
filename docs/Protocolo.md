# Proyecto Cliente-Servidor: Chat Colaborativo con Salas Temáticas

## 1. Introducción
El presente documento describe el protocolo de comunicación utilizado entre el cliente y el servidor dentro del proyecto Chat Colaborativo con Salas Temáticas, desarrollado en el marco de la asignatura Arquitectura Cliente–Servidor.

El objetivo de este protocolo es establecer un formato claro, simple y estándar para el intercambio de mensajes entre los componentes del sistema.
El diseño se basa en un modelo textual por comandos, donde cada instrucción y respuesta sigue una estructura definida, facilitando así la interpretación por parte de ambos extremos de la comunicación.

Este enfoque, inspirado en el documento de “Servicios” del profesor, utiliza sockets TCP y permite mantener una conexión persistente y bidireccional durante toda la sesión.

## 2.Estructura General del Protocolo

El protocolo define que todo mensaje enviado entre cliente y servidor esté formado por una palabra clave (comando) seguida de uno o más parámetros, separados por el carácter #.
Cada mensaje debe iniciar y terminar con este delimitador, lo que facilita la segmentación y el análisis en la recepción.

El formato general de un mensaje es:

#COMANDO#parametro1#parametro2#...#

Ejemplos:

#CONECTAR#Leidy#
#MENSAJE#General#Hola a todos#

Este formato mantiene la simplicidad del modelo de “servicios” propuesto, garantizando la compatibilidad entre distintos clientes y servidores.

## 3.Comandos del Cliente
Los comandos que puede enviar un cliente son los siguientes:

#CONECTAR#nombre# → Establece la conexión del usuario con el servidor utilizando un nombre único.

#CREAR_SALA#nombreSala# → Solicita la creación de una nueva sala de chat temática.

#UNIR_SALA#nombreSala# → Permite unirse a una sala existente.

#MENSAJE#sala#texto# → Envía un mensaje al resto de los usuarios dentro de la sala seleccionada.

#SALIR_SALA#nombreSala# → Informa al servidor que el usuario abandona la sala.

#DESCONECTAR# → Finaliza la conexión del cliente con el servidor.

Cada uno de estos comandos sigue el formato textual definido y puede ser interpretado sin ambigüedad por el servidor.

## 4.Respuestas del Servidor

El servidor utiliza el mismo esquema estructural para devolver respuestas a los clientes, ya sean mensajes de confirmación, error o notificaciones automáticas.

Entre los comandos más comunes se encuentran:

#OK#mensaje# → Indica que la acción solicitada se ejecutó correctamente.

#ERROR#descripcion# → Señala que ocurrió un error o que el comando enviado fue inválido.

#MENSAJE#sala#usuario#texto# → Reenvía los mensajes enviados dentro de una sala a todos los usuarios conectados en ella.

#USUARIO_ENTRO#sala#usuario# → Notifica que un nuevo participante se unió a la sala.

#USUARIO_SALIO#sala#usuario# → Informa que un usuario abandonó la sala.

#LISTA_SALAS#sala1,sala2,...# → Devuelve la lista de salas activas en el servidor.

## 5.Reglas del Protocolo
El funcionamiento correcto de la comunicación depende del cumplimiento de las siguientes reglas:

Todos los mensajes deben transmitirse en formato de texto plano codificado en UTF-8.

Cada comando debe iniciar y finalizar con el carácter #.

Los nombres de usuario deben ser únicos durante la sesión activa.

El servidor debe responder a cada solicitud del cliente, confirmando su ejecución con #OK# o informando un error con #ERROR#.

Los comandos no reconocidos o mal formados deben generar la respuesta #ERROR#Comando inválido#.

El flujo de comunicación se mantiene abierto hasta que el cliente envía el comando #DESCONECTAR#.

Estas reglas aseguran la uniformidad del intercambio de datos y evitan inconsistencias en el manejo de sesiones y mensajes.

## 6.Flujo de Comunicación General

El ciclo de comunicación típico entre un cliente y el servidor se desarrolla de la siguiente manera:

El cliente inicia la aplicación y se conecta al servidor mediante socket TCP.

Envía el comando #CONECTAR#usuario# con su nombre de usuario.

El servidor valida la conexión y responde con #OK#Conectado#.

El cliente puede crear o unirse a una sala usando los comandos #CREAR_SALA# o #UNIR_SALA#.

Los mensajes enviados desde un cliente son recibidos por el servidor y retransmitidos al resto de los usuarios de la misma sala.

Cuando un usuario se desconecta, el servidor notifica al resto mediante #USUARIO_SALIO#sala#usuario#.

Finalmente, el servidor registra los mensajes y mantiene actualizado el historial de la conversación.

