from cliente.nucleo_cliente import ClienteChat

cliente = ClienteChat(host="127.0.0.1", puerto=5000)
cliente.conectar("Miguel")

cliente.enviar_comando("#CREAR_SALA#General#")
cliente.enviar_comando("#UNIR_SALA#General#")
cliente.enviar_comando("#MENSAJE#General#Hola a todos!#")