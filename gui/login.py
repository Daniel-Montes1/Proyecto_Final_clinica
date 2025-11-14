"""
login.py
-----------------------------------
Ventana de inicio de sesión para el sistema ECG Clínica del Corazón.
Permite ingresar con usuario y contraseña. Dependiendo del rol
almacenado en usuarios.json, se redirige a la interfaz correspondiente.
"""

import tkinter as tk
from tkinter import  messagebox
import json
from .admin_gui import AdminWindow
from .doctor_gui import DoctorWindow
from .paciente_gui import PacienteWindow

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg="#fff")
        self.root.geometry("400x520")
        # Cabecera con imagen cuadrada y centrada
        header = tk.Frame(self.root, bg="#b71c1c", height=220)
        header.pack(fill="x", side="top")
        try:
            from PIL import Image, ImageTk
            img = Image.open("gui/cabecera.png")
            img = img.resize((200, 200))
            self.header_img = ImageTk.PhotoImage(img)
            tk.Label(header, image=self.header_img, bg="#b71c1c").pack(pady=10)
        except Exception:
            tk.Label(header, text="CLÍNICA ECG", font=("Arial", 24, "bold"), fg="#fff", bg="#b71c1c").pack(pady=40)

        # Cuerpo blanco con formulario
        form = tk.Frame(self.root, bg="#fff", padx=24, pady=18)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Bienvenido/a", font=("Arial", 16, "bold"), fg="#b71c1c", bg="#fff").pack(pady=(8, 2))
        tk.Label(form, text="Inicia sesión para continuar", font=("Arial", 11), fg="#333", bg="#fff").pack(pady=(0, 16))

        tk.Label(form, text="Usuario", font=("Arial", 10), fg="#b71c1c", bg="#fff").pack(anchor="w")
        self.username_entry = tk.Entry(form, font=("Arial", 11), bg="#fff", fg="#222", relief="solid", bd=1, highlightthickness=0, insertbackground="#222")
        self.username_entry.pack(fill="x", pady=(0, 10))

        tk.Label(form, text="Contraseña", font=("Arial", 10), fg="#b71c1c", bg="#fff").pack(anchor="w")
        self.password_entry = tk.Entry(form, show="*", font=("Arial", 11), bg="#fff", fg="#222", relief="solid", bd=1, highlightthickness=0, insertbackground="#222")
        self.password_entry.pack(fill="x", pady=(0, 18))

        login_btn = tk.Button(form, text="Iniciar Sesión", command=self.validate_login, font=("Arial", 11, "bold"), bg="#b71c1c", fg="#fff", activebackground="#d32f2f", activeforeground="#fff", relief="flat", height=2)
        login_btn.pack(fill="x", pady=(0, 8))

        # Pie de página
        tk.Label(form, text="© Clínica del Corazón 2025", font=("Arial", 8), fg="#888", bg="#fff").pack(side="bottom", pady=(18, 0))

    def validate_login(self):
        usuario = self.username_entry.get()
        contraseña = self.password_entry.get()

        try:
            with open('data/usuarios.json', 'r') as f:
                users = json.load(f)
            
            # Modificado para usar los campos correctos de tu JSON
            user = next((u for u in users if u['usuario'] == usuario and u['contrasena'] == contraseña), None)
            
            if user:
                self.root.withdraw()  # Oculta ventana de login
                if user['rol'] == 'admin':
                    new_window = tk.Toplevel()
                    new_window.title(f"Clínica del Corazón - {user['rol'].capitalize()}")
                    new_window.geometry("800x600")
                    AdminWindow(new_window)
                    new_window.protocol("WM_DELETE_WINDOW", self.root.destroy)
                elif user['rol'] == 'doctor':
                    DoctorWindow(self.root, user['usuario'])
                elif user['rol'] == 'paciente':
                    PacienteWindow(self.root, user['usuario'])
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar sesión: {str(e)}")


    def redirigir(self, rol, usuario):
        """Abre la ventana según el rol."""
        self.root.withdraw()  # Oculta ventana de login

        if rol == "admin":
            nueva_ventana = tk.Toplevel()
            AdminWindow(nueva_ventana, usuario)
        elif rol == "doctor":
            nueva_ventana = tk.Toplevel()
            DoctorWindow(nueva_ventana, rol["usuario"])
        elif rol == "paciente":
            nueva_ventana = tk.Toplevel()
            PacienteWindow(nueva_ventana, rol["usuario"])
        else:
            messagebox.showerror("Error", f"Rol desconocido: {rol}")
            self.root.deiconify()  # Muestra el login de nuevo
