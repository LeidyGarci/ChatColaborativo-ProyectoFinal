# Proyecto Cliente-Servidor: Chat Colaborativo con Salas Temáticas

## 1. Introducción
El presente documento describe la especificación funcional y técnica del sistema **Chat Colaborativo con Salas Temáticas**, diseñado como parte del desarrollo académico de la asignatura *Arquitectura Cliente–Servidor*.  

El propósito de este proyecto es construir una aplicación de chat en red local, donde varios usuarios puedan conectarse simultáneamente para comunicarse en tiempo real dentro de diferentes salas temáticas.  

El sistema se implementa bajo una arquitectura **cliente-servidor**, utilizando **sockets TCP** y **hilos (threading)** para manejar múltiples conexiones concurrentes.  

---

## 2. Objetivo General
Diseñar e implementar un sistema de comunicación en tiempo real que permita la interacción de varios usuarios en salas de chat temáticas, garantizando la gestión ordenada de mensajes, usuarios y salas mediante una arquitectura cliente-servidor.

---

## 3. Objetivos Específicos
- Implementar un **servidor multihilo** capaz de aceptar múltiples conexiones TCP de manera simultánea.  
- Desarrollar un **cliente gráfico** en **Tkinter** que permita conectarse al servidor, crear o unirse a salas y enviar mensajes.  
- Definir un **protocolo de comunicación** basado en comandos simples de texto para estandarizar los mensajes entre el cliente y el servidor.  
- Crear un mecanismo de **almacenamiento persistente** utilizando archivos JSON para registrar los historiales de chat.  
- Incluir una **validación básica de seguridad**, garantizando que cada usuario tenga un nombre único durante la sesión.  
- Documentar completamente la arquitectura, los flujos y los componentes mediante diagramas UML y descripciones técnicas.

---

## 4. Arquitectura del Sistema
El sistema está compuesto por dos elementos principales: el **servidor** y los **clientes**.

El **servidor** se encarga de recibir y gestionar las conexiones, mantener el control de los usuarios conectados y las salas activas, distribuir los mensajes a los participantes de cada sala y registrar los historiales en un archivo JSON.  
Cada cliente conectado se maneja en un hilo independiente, permitiendo la comunicación simultánea entre varios usuarios.

El **cliente** es una aplicación que se conecta al servidor mediante socket TCP.  
Desde la interfaz gráfica desarrollada con **Tkinter**, el usuario podrá ingresar su nombre, seleccionar o crear una sala de chat, enviar y recibir mensajes, así como desconectarse cuando lo desee.  

Ambos componentes se comunican mediante un **protocolo textual** estructurado por comandos delimitados con el carácter `#`, lo cual facilita la interpretación de las órdenes tanto del lado del cliente como del servidor.

---

## 5. Requisitos Funcionales
El sistema debe permitir que varios usuarios se conecten al mismo tiempo, cada uno identificado con un nombre único.  
El servidor debe ofrecer la posibilidad de crear nuevas salas de chat y permitir que los usuarios se unan o abandonen las ya existentes.  
Dentro de cada sala, los mensajes deben transmitirse en tiempo real a todos los participantes.  
Además, el sistema debe mostrar los usuarios conectados, notificar las entradas y salidas de participantes, y guardar un historial de los mensajes enviados.  

El servidor también debe manejar de forma ordenada la desconexión de los usuarios, eliminándolos de las listas de salas y notificando su salida a los demás miembros.

---

## 6. Requisitos No Funcionales
El sistema debe garantizar una comunicación **bidireccional y estable** entre los clientes y el servidor utilizando sockets TCP.  
Debe tener una **baja latencia**, de manera que los mensajes se transmitan casi instantáneamente.  
El servidor debe estar diseñado para soportar un número variable de usuarios mediante **concurrencia por hilos**.  
La interfaz del cliente debe ser sencilla, clara y amigable, para que cualquier usuario pueda comprender su funcionamiento sin instrucciones adicionales.  
Asimismo, el sistema debe contar con un control básico de errores y de nombres duplicados, y continuar funcionando aun si uno de los clientes se desconecta inesperadamente.

---

## 7. Flujo General del Sistema
1. El servidor se inicia y queda a la espera de conexiones entrantes.  
2. Cada cliente que inicia la aplicación ingresa su nombre de usuario y establece conexión con el servidor.  
3. Una vez conectado, el cliente puede crear una nueva sala temática o unirse a alguna existente.  
4. Cuando un usuario se une a una sala, el servidor lo registra y notifica al resto de los participantes.  
5. Cada mensaje enviado por un usuario se recibe primero en el servidor, el cual lo retransmite inmediatamente a todos los clientes de la misma sala.  
6. Si un usuario cierra la aplicación o se desconecta, el servidor actualiza la lista de usuarios y notifica al resto que el participante ha salido.  
7. Paralelamente, el servidor registra todos los mensajes en un archivo JSON ubicado en la carpeta `datos`, preservando así el historial de conversación.

---

## 8. Componentes del Sistema
El proyecto se organiza en una estructura de carpetas clara y modular.  
El **servidor** contiene los módulos encargados de la conexión, la gestión de usuarios, el almacenamiento del historial y el protocolo de comunicación.  
El **cliente** contiene los módulos que implementan la interfaz gráfica, el manejo del protocolo y la comunicación con el servidor.  
Finalmente, existe una carpeta `docs` con toda la documentación técnica y los diagramas UML del sistema.  

Entre los archivos más importantes se encuentran:
- `servidor/main.py`: punto de inicio del servidor TCP.  
- `servidor/nucleo_servidor.py`: contiene la lógica principal para manejar usuarios y salas.  
- `cliente/interfaz.py`: implementa la interfaz gráfica con Tkinter.  
- `cliente/nucleo_cliente.py`: gestiona el envío y recepción de mensajes.  
- `datos/historial.json`: archivo donde se guarda el registro de los mensajes enviados en las salas.  

---

## 9. Conclusión
El proyecto **Chat Colaborativo con Salas Temáticas** permite integrar de manera práctica los conceptos fundamentales de la programación cliente-servidor, la comunicación por sockets, el manejo de hilos, la concurrencia y la persistencia de datos.
  
Su desarrollo contribuye al entendimiento de cómo se estructuran las aplicaciones distribuidas, enfatizando la importancia de la coordinación entre múltiples procesos, la sincronización de datos y la arquitectura modular.  
Además, su diseño claro y documentado facilita la comprensión del flujo de información y la futura ampliación de sus funcionalidades.
