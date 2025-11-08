"""
chat_app.py — Interfaz gráfica del cliente de chat

Este archivo implementa la GUI del cliente de chat colaborativo usando Tkinter.
Permite al usuario conectarse al servidor, unirse o crear salas temáticas,
enviar y recibir mensajes, y ver los usuarios conectados.

Clases principales:
- ChatApp: Ventana principal que controla la navegación entre diferentes frames.
- LoginFrame: Frame de inicio de sesión del usuario.
- MainMenuFrame: Frame de menú principal con opciones de salas, creación de sala y lista de usuarios.
- RoomsFrame: Frame para mostrar y unirse a salas existentes.
- ChatFrame: Frame para visualizar el chat de una sala y enviar mensajes.
- UsersFrame: Frame que muestra los usuarios conectados al servidor.

Constantes de color:
- BG: Color de fondo principal.
- FG: Color de texto principal.
- ACCENT: Color de botones principales.
- WHITE: Color blanco (para texto en botones).
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from nucleo_cliente import BackendCliente

# -------------------- COLORES --------------------
BG = "#EAF2FB"       # Fondo principal
FG = "#052744"       # Texto principal
ACCENT = "#1479E0"   # Botones de acción
WHITE = "#FFFFFF"    # Texto blanco para botones

# ==================== CLASE PRINCIPAL ====================
class ChatApp(tk.Tk):
    """
    Ventana principal de la aplicación de chat.
    Gestiona la interacción entre los frames y el backend del cliente.
    """

    def __init__(self):
        super().__init__()
        self.title("Chat Colaborativo - Salas Temáticas UTP")
        self.geometry("820x560")
        self.configure(bg=BG)

        # Backend que maneja la conexión con el servidor
        self.backend = BackendCliente()

        # -------------------- FRAMES --------------------
        # Frames principales
        self.login_frame = LoginFrame(self, self.backend)
        self.main_frame = MainMenuFrame(
            self, self.backend, self.go_rooms, self.go_create, self.go_users
        )
        self.rooms_frame = RoomsFrame(self, self.backend, self.enter_room, self.go_main_menu)
        self.chat_frame = ChatFrame(self, self.backend, self.leave_room)
        self.users_frame = UsersFrame(self, self.backend, self.go_main_menu)

        # Mostrar login al iniciar
        self.login_frame.pack(fill="both", expand=True)

        # Llamada periódica para procesar mensajes del backend
        self.after(200, self.poll_backend)

    # -------------------- MÉTODOS DE BACKEND --------------------
    def poll_backend(self):
        """
        Procesa los mensajes recibidos desde el backend.
        Se ejecuta periódicamente con 'after'.
        """
        q = self.backend.queue
        try:
            while True:
                comando, datos = q.get_nowait()

                if comando == "OK":
                    messagebox.showinfo("Servidor", datos)
                    # Si se unió a una sala, mostrar chat
                    if "Te has unido a la sala" in datos and self.backend.sala_actual:
                        self.chat_frame.set_room(self.backend.sala_actual)
                        self.show_frame(self.chat_frame)

                elif comando == "ERROR":
                    messagebox.showerror("Error", datos)

                elif comando == "INFO":
                    self.chat_frame.append_message(datos)

                elif comando == "ROOM_LIST":
                    self.rooms_frame.update_rooms(datos)

                elif comando == "USER_LIST_ALL":
                    self.users_frame.update_users(datos)

                elif comando in ("CHAT", "NOTIFY"):
                    if datos.startswith("CHAT#") or datos.startswith("NOTIFY#"):
                        datos = datos.split("#", 1)[1]
                    self.chat_frame.append_message(datos)

                elif comando == "DISCONNECTED":
                    messagebox.showwarning("Desconectado", datos)
                    self.backend.disconnect()
                    self.show_frame(self.login_frame)

                else:
                    # Mensajes no reconocidos se muestran en el chat
                    self.chat_frame.append_message(f"[{comando}] {datos}")

        except:
            pass
        finally:
            # Re-ejecutar periódicamente
            self.after(200, self.poll_backend)

    def show_frame(self, frame):
        """
        Muestra solo el frame indicado, ocultando los demás.
        """
        for f in (self.login_frame, self.main_frame, self.rooms_frame, self.chat_frame, self.users_frame):
            f.pack_forget()
        frame.pack(fill="both", expand=True)

    # -------------------- NAVEGACIÓN ENTRE FRAMES --------------------
    def go_main_menu(self):
        """Mostrar el menú principal."""
        self.show_frame(self.main_frame)

    def go_rooms(self):
        """Solicitar lista de salas al backend y mostrar frame de salas."""
        self.backend.request_rooms()
        self.show_frame(self.rooms_frame)

    def go_create(self):
        """Crear una nueva sala mediante diálogo."""
        nombre = simpledialog.askstring("Crear sala", "Nombre de la nueva sala:", parent=self)
        if nombre:
            nombre = nombre.strip()
            if nombre:
                self.backend.join_room(nombre)

    def go_users(self):
        """Solicitar lista de usuarios y mostrar frame de usuarios."""
        self.backend.request_users()
        self.show_frame(self.users_frame)

    def enter_room(self, sala):
        """Unirse a la sala seleccionada."""
        self.backend.join_room(sala)

    def leave_room(self):
        """Salir de la sala actual y volver al menú principal."""
        self.backend.leave_room()
        self.show_frame(self.main_frame)

    def set_username_and_connect(self, nombre):
        """
        Conectar al servidor con el nombre proporcionado.
        Muestra mensajes de error si falla.
        """
        ok, msg = self.backend.conectar(nombre)
        if not ok:
            messagebox.showerror("Conexión", msg)
            return
        self.main_frame.set_username(nombre)
        self.show_frame(self.main_frame)


# ==================== FRAMES DE LA INTERFAZ ====================

class LoginFrame(tk.Frame):
    """Frame de inicio de sesión del usuario."""
    def __init__(self, root, backend):
        super().__init__(root, bg=BG, padx=20, pady=20)
        self.backend = backend

        tk.Label(self, text="Bienvenido al Chat de Salas Temáticas UTP",
                 font=("Helvetica", 18, "bold"), bg=BG, fg=FG).pack(pady=(20,10))
        tk.Label(self, text="Ingresa tu nombre de usuario para comenzar",
                 bg=BG, fg=FG).pack(pady=(0,20))

        self.entry = tk.Entry(self, font=("Helvetica",14))
        self.entry.pack(ipadx=50, ipady=8)
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self.ingresar())

        tk.Button(self, text="Ingresar", command=self.ingresar,
                  bg=ACCENT, fg=WHITE, relief="flat", padx=12, pady=6).pack(pady=20)

    def ingresar(self):
        """Obtiene el nombre de usuario e intenta conectarse."""
        nombre = self.entry.get().strip()
        if not nombre:
            messagebox.showwarning("Nombre requerido", "Por favor ingresa un nombre de usuario.")
            return
        self.master.set_username_and_connect(nombre)


class MainMenuFrame(tk.Frame):
    """Frame de menú principal del usuario."""
    def __init__(self, root, backend, go_rooms_cb, go_create_cb, go_users_cb):
        super().__init__(root, bg=BG, padx=20, pady=20)
        self.backend = backend
        self.go_rooms_cb = go_rooms_cb
        self.go_create_cb = go_create_cb
        self.go_users_cb = go_users_cb

        self.lbl_welcome = tk.Label(self, text="", font=("Helvetica",16,"bold"), bg=BG, fg=FG)
        self.lbl_welcome.pack(pady=(20,10))
        tk.Label(self, text="Opciones", font=("Helvetica",14), bg=BG, fg=FG).pack(pady=(0,6))

        frame = tk.Frame(self, bg=BG)
        frame.pack(pady=10)
        tk.Button(frame, text="Salas Temáticas", command=self.go_rooms_cb, width=20,
                  bg=ACCENT, fg=WHITE).grid(row=0,column=0,pady=6,padx=6)
        tk.Button(frame, text="Crear Sala", command=self.go_create_cb, width=20,
                  bg=ACCENT, fg=WHITE).grid(row=1,column=0,pady=6,padx=6)
        tk.Button(frame, text="Usuarios Conectados", command=self.go_users_cb, width=20,
                  bg=ACCENT, fg=WHITE).grid(row=2,column=0,pady=6,padx=6)

    def set_username(self, nombre):
        """Actualiza el mensaje de bienvenida con el nombre del usuario."""
        self.lbl_welcome.config(text=f"Bienvenido a las salas de chat — Usuario: {nombre}")


class RoomsFrame(tk.Frame):
    """Frame que muestra las salas existentes y permite unirse a ellas."""
    def __init__(self, root, backend, join_cb, back_cb):
        super().__init__(root, bg=BG, padx=12, pady=12)
        self.backend = backend
        self.join_cb = join_cb
        self.back_cb = back_cb

        tk.Label(self, text="Salas Temáticas Disponibles", font=("Helvetica",16,"bold"),
                 bg=BG, fg=FG).pack(pady=(8,6))
        self.listbox = tk.Listbox(self, font=("Helvetica",12), height=12)
        self.listbox.pack(fill="both", expand=False, padx=10)

        frame = tk.Frame(self, bg=BG)
        frame.pack(pady=10)
        tk.Button(frame, text="Entrar a la sala", command=self.entrar,
                  bg=ACCENT, fg=WHITE).grid(row=0,column=0,padx=8)
        tk.Button(frame, text="Refrescar", command=self.refrescar, bg="lightgray").grid(row=0,column=1,padx=8)
        tk.Button(frame, text="Volver", command=self.back_cb, bg="lightgray").grid(row=0,column=2,padx=8)

    def update_rooms(self, lista_texto):
        """Actualiza la lista de salas mostradas en el Listbox."""
        self.listbox.delete(0,tk.END)
        if not lista_texto:
            return
        salas = [s.strip() for s in lista_texto.split(",") if s.strip()]
        for s in salas:
            self.listbox.insert(tk.END, s)

    def refrescar(self):
        """Solicita al backend la lista de salas actualizada."""
        self.backend.request_rooms()

    def entrar(self):
        """Entra a la sala seleccionada en el Listbox."""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Seleccionar sala", "Selecciona una sala primero.")
            return
        sala = self.listbox.get(sel[0])
        self.join_cb(sala)


class ChatFrame(tk.Frame):
    """Frame de chat de una sala, mostrando mensajes y permitiendo enviar."""
    def __init__(self, root, backend, leave_cb):
        super().__init__(root, bg=BG, padx=12, pady=12)
        self.backend = backend
        self.leave_cb = leave_cb
        self.sala = None

        # Cabecera con nombre de sala y botón de salir
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x")
        self.lbl_room = tk.Label(header, text="Sala: —", font=("Helvetica",14,"bold"), bg=BG, fg=FG)
        self.lbl_room.pack(side="left")
        tk.Button(header, text="Salir de sala", command=self.leave_cb, bg="lightgray").pack(side="right")

        # Área de texto del chat (solo lectura)
        self.txt_chat = tk.Text(self, wrap="word", state="disabled", height=20)
        self.txt_chat.pack(fill="both", expand=True, padx=6, pady=10)

        # Entrada de mensaje y botón enviar
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="x", pady=(0,10))
        self.entry_msg = tk.Entry(frame, font=("Helvetica",12))
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(6,4))
        self.entry_msg.bind("<Return>", lambda e: self.enviar_msg())
        tk.Button(frame, text="Enviar", command=self.enviar_msg, bg=ACCENT, fg=WHITE).pack(side="right", padx=6)

    def set_room(self, sala):
        """Configura el chat para la sala seleccionada y limpia el contenido previo."""
        self.sala = sala
        self.lbl_room.config(text=f"Sala: {sala}")
        self.txt_chat.config(state="normal")
        self.txt_chat.delete("1.0",tk.END)
        self.txt_chat.config(state="disabled")

    def append_message(self, texto):
        """Agrega un mensaje al área de chat."""
        if texto.startswith("CHAT#") or texto.startswith("NOTIFY#"):
            texto = texto.split("#",1)[1]
        self.txt_chat.config(state="normal")
        self.txt_chat.insert(tk.END, texto.strip()+"\n")
        self.txt_chat.see(tk.END)
        self.txt_chat.config(state="disabled")

    def enviar_msg(self):
        """Envía el mensaje ingresado al backend y limpia la entrada."""
        texto = self.entry_msg.get().strip()
        if not texto:
            return
        self.backend.send_message(texto)
        self.entry_msg.delete(0,tk.END)


class UsersFrame(tk.Frame):
    """Frame que muestra los usuarios conectados y su sala."""
    def __init__(self, root, backend, back_cb):
        super().__init__(root, bg=BG, padx=12, pady=12)
        self.backend = backend
        self.back_cb = back_cb

        tk.Label(self, text="Usuarios Conectados", font=("Helvetica",16,"bold"), bg=BG, fg=FG).pack(pady=(8,6))
        self.listbox = tk.Listbox(self, font=("Helvetica",12), height=16)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0,10))
        tk.Button(self, text="Volver", command=self.back_cb, bg="lightgray").pack(pady=(0,6))

    def update_users(self, texto):
        """Actualiza la lista de usuarios conectados."""
        self.listbox.delete(0,tk.END)
        if not texto:
            return
        usuarios = [u.strip() for u in texto.split(",") if u.strip()]
        for u in usuarios:
            self.listbox.insert(tk.END, u)
