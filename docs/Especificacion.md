# Especificación del Programa “Chat Colaborativo – Salas Temáticas UTP”

## 1. Planteamiento del problema
El objetivo del proyecto es crear un sistema de chat colaborativo que permita:
- Conexión de múltiples usuarios.
- Creación y unión a salas temáticas.
- Comunicación en tiempo real dentro de cada sala.
- Registro de mensajes (historial) por sala.
- Visualización de usuarios conectados y salas activas.
- Manejo seguro de concurrencia y comunicación cliente-servidor.

Se planteó un modelo cliente-servidor, donde el cliente maneja la interfaz gráfica y la interacción del usuario, y el servidor gestiona salas, usuarios y persistencia de mensajes.

## 2. Enfoque de diseño
Se utilizó un enfoque modular y orientado a objetos:
- Separación entre GUI (`interfaz.py`) y lógica de comunicación (`nucleo_cliente.py`) en el cliente.
- Servidor centralizado que gestiona usuarios, salas y mensajes (`nucleo_servidor.py`).
- Definición de protocolos de comunicación (`ProtocoloCliente`, `ProtocoloServidor`).
- Persistencia de mensajes mediante JSON (`almacenamiento.py`).

Los beneficios de este enfoque son bajo acoplamiento, escalabilidad para futuras funcionalidades y concurrencia segura con threading y locks.

## 3. Arquitectura del sistema

Cliente:
- `main.py`: ejecuta la aplicación GUI.
- `interfaz.py`: GUI completa (Login, Menú, Salas, Chat, Usuarios).
- `nucleo_cliente.py`: `BackendCliente` maneja sockets, eventos y cola para GUI.
- `protocolo_cliente.py`: procesa mensajes entrantes `COMANDO#DATOS`.
- `config.py`: host, puerto, buffer, codificación y mensajes de bienvenida.

Servidor:
- `nucleo_servidor.py`: `ServidorChat` administra usuarios, salas y retransmisión de mensajes.
- `protocolo.py`: define comandos y estructura de mensajes.
- `almacenamiento.py`: clase `Almacenamiento` guarda mensajes en JSON con bloqueo seguro.
- `config.py`: host, puerto, buffer, codificación y ruta de historial.
- `datos/historial.json`: archivo de historial de mensajes.

## 4. Flujo de funcionamiento
1. Usuario ingresa su nombre en la GUI.
2. Backend conecta al servidor con `HELLO#nombre`.
3. Servidor valida nombre y confirma conexión con `OK`.
4. Usuario puede:
   - Unirse/crear una sala (`JOIN_SALA#nombre_sala`).
   - Enviar mensajes (`MSG#texto`) que se retransmiten a todos y se guardan.
   - Solicitar listas de usuarios (`USER_LIST`/`USER_LIST_ALL`) y salas (`ROOM_LIST`).
   - Salir de una sala (`LEAVE_SALA`) o desconectarse (`SALIR`).
5. Backend recibe respuestas del servidor y actualiza GUI en tiempo real mediante la cola `queue.Queue()`.

## 5. Cumplimiento de requerimientos
- Separación GUI y lógica de comunicación lograda con `interfaz.py` y `nucleo_cliente.py`.
- Modelo cliente-servidor implementado con `BackendCliente` y `ServidorChat` usando sockets TCP.
- Múltiples salas y usuarios concurrentes gestionados con `threading` y locks.
- Historial persistente implementado en `Almacenamiento` guardando mensajes por sala en JSON.
- Protocolos claros definidos en `ProtocoloCliente` y `ProtocoloServidor`.
- Manejo de errores y desconexiones notificado en la GUI y gestionado en el backend.
- Modularidad y escalabilidad, permitiendo agregar nuevas funcionalidades sin cambiar toda la estructura.

## 6. Decisiones de diseño clave
- Uso de `queue.Queue()` en BackendCliente para actualizar GUI de forma segura en hilos.
- Locks en ServidorChat y Almacenamiento para evitar condiciones de carrera.
- Historial por sala permite mostrar mensajes previos al entrar.
- Protocolo `COMANDO#DATOS` fácil de extender a nuevos comandos.
- Notificaciones de eventos (`NOTIFY`) para informar a los usuarios de cambios en la sala.

## 7. Conclusión
El programa cumple con los objetivos planteados:
- Soporta múltiples usuarios y comunicación en tiempo real.
- Gestiona salas dinámicas y mantiene historial de mensajes.
- Diseño modular, seguro y escalable.
- Implementa protocolos claros y manejo de errores.
- Preparado para presentación y documentación profesional.
