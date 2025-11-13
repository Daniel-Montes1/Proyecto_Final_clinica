"""
admin_gui.py
-----------------------------------
Interfaz del Admin del sistema ECG Clínica del Corazón.
Permite crear, actualizar, eliminar y listar usuarios del sistema.

Los datos se guardan en data/usuarios.json
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json

class AdminWindow:
    def __init__(self, root):
        self.root = root
        self.users_file = "data/usuarios.json"
        self.current_users = self.load_users()
        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg="#fff")
        self.root.geometry("900x600")
        # Cabecera gráfica
        header = tk.Frame(self.root, bg="#b71c1c", height=120)
        header.pack(fill="x", side="top")
        try:
            from PIL import Image, ImageTk
            img = Image.open("gui/cabecera.png")
            img = img.resize((90, 90))
            self.header_img = ImageTk.PhotoImage(img)
            tk.Label(header, image=self.header_img, bg="#b71c1c").pack(pady=10)
        except Exception:
            tk.Label(header, text="CLÍNICA ECG", font=("Arial", 22, "bold"), fg="#fff", bg="#b71c1c").pack(pady=20)

        # Título
        tk.Label(self.root, text="Panel de Administración", font=("Arial", 16, "bold"), fg="#b71c1c", bg="#fff").pack(pady=(0, 8))

        # Frame principal blanco
        self.main_frame = tk.Frame(self.root, bg="#fff", padx=18, pady=10)
        self.main_frame.pack(fill="both", expand=True)

        # Lista de usuarios (Treeview)
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#b71c1c", foreground="#fff")
        self.tree = ttk.Treeview(self.main_frame, columns=('ID', 'Nombre', 'Rol', 'Documento'), show='headings', height=12)
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nombre', text='Nombre')
        self.tree.heading('Rol', text='Rol')
        self.tree.heading('Documento', text='Documento')
        self.tree.column('ID', width=80, anchor='center')
        self.tree.column('Nombre', width=180, anchor='center')
        self.tree.column('Rol', width=100, anchor='center')
        self.tree.column('Documento', width=120, anchor='center')
        self.tree.pack(fill="x", pady=(8, 16))

        # Botones CRUD (en una fila)
        btn_frame = tk.Frame(self.main_frame, bg="#fff")
        btn_frame.pack(fill="x", pady=(0, 8))
        btn_style = {"font": ("Arial", 11, "bold"), "bg": "#b71c1c", "fg": "#fff", "activebackground": "#d32f2f", "activeforeground": "#fff", "relief": "flat", "height": 2}
        tk.Button(btn_frame, text="Crear Usuario", command=self.show_create_window, **btn_style).pack(side="left", expand=True, fill="x", padx=4)
        tk.Button(btn_frame, text="Actualizar Usuario", command=self.show_update_window, **btn_style).pack(side="left", expand=True, fill="x", padx=4)
        tk.Button(btn_frame, text="Eliminar Usuario", command=self.delete_user, **btn_style).pack(side="left", expand=True, fill="x", padx=4)
        tk.Button(btn_frame, text="Refrescar Lista", command=self.refresh_users, **btn_style).pack(side="left", expand=True, fill="x", padx=4)
        tk.Button(btn_frame, text="Salir", command=self.root.destroy, **btn_style).pack(side="left", expand=True, fill="x", padx=4)

        self.refresh_users()

    def load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return []

    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.current_users, f, indent=4)

    def refresh_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.current_users = self.load_users()
        for user in self.current_users:
            self.tree.insert('', 'end', values=(
                user.get('id', ''),
                user.get('nombre', ''),
                user.get('rol', ''),
                user.get('documento', '')
            ))

    def show_create_window(self):
        create_window = tk.Toplevel(self.root)
        create_window.title("Crear Usuario")
        create_window.geometry("400x560")
        create_window.configure(bg="#fff")

        # Cabecera
        header = tk.Frame(create_window, bg="#b71c1c", height=90)
        header.pack(fill="x", side="top")
        try:
            from PIL import Image, ImageTk
            img = Image.open("gui/cabecera.png")
            img = img.resize((60, 60))
            header_img = ImageTk.PhotoImage(img)
            tk.Label(header, image=header_img, bg="#b71c1c").pack(pady=8)
            create_window.header_img = header_img
        except Exception:
            tk.Label(header, text="CLÍNICA ECG", font=("Arial", 16, "bold"), fg="#fff", bg="#b71c1c").pack(pady=16)

        tk.Label(create_window, text="Crear Usuario", font=("Arial", 14, "bold"), fg="#b71c1c", bg="#fff").pack(pady=(0, 8))

        form = tk.Frame(create_window, bg="#fff", padx=18, pady=10)
        form.pack(fill="both", expand=True)

        label_style = {"font": ("Arial", 10), "fg": "#b71c1c", "bg": "#fff"}
        entry_style = {"font": ("Arial", 11), "bg": "#fff", "fg": "#222", "relief": "solid", "bd": 1, "highlightthickness": 0, "insertbackground": "#222"}

        tk.Label(form, text="Rol", **label_style).grid(row=0, column=0, pady=5, sticky="w")
        rol_combo = ttk.Combobox(form, values=['admin', 'doctor', 'paciente'], state="readonly", font=("Arial", 11))
        rol_combo.grid(row=0, column=1, pady=5, sticky="ew")

        tk.Label(form, text="ID", **label_style).grid(row=1, column=0, pady=5, sticky="w")
        id_var = tk.StringVar()
        id_entry = tk.Entry(form, textvariable=id_var, state="readonly", **entry_style)
        id_entry.grid(row=1, column=1, pady=5, sticky="ew")

        tk.Label(form, text="Usuario", **label_style).grid(row=2, column=0, pady=5, sticky="w")
        usuario_entry = tk.Entry(form, **entry_style)
        usuario_entry.grid(row=2, column=1, pady=5, sticky="ew")

        tk.Label(form, text="Contraseña", **label_style).grid(row=3, column=0, pady=5, sticky="w")
        pass_entry = tk.Entry(form, show="*", **entry_style)
        pass_entry.grid(row=3, column=1, pady=5, sticky="ew")

        tk.Label(form, text="Nombre", **label_style).grid(row=4, column=0, pady=5, sticky="w")
        nombre_entry = tk.Entry(form, **entry_style)
        nombre_entry.grid(row=4, column=1, pady=5, sticky="ew")

        tk.Label(form, text="Documento", **label_style).grid(row=5, column=0, pady=5, sticky="w")
        doc_entry = tk.Entry(form, **entry_style)
        doc_entry.grid(row=5, column=1, pady=5, sticky="ew")

        tk.Label(form, text="Edad", **label_style).grid(row=6, column=0, pady=5, sticky="w")
        edad_entry = tk.Entry(form, **entry_style)
        edad_entry.grid(row=6, column=1, pady=5, sticky="ew")

        # Campos específicos (se agregan dinámicamente)
        espec_label = tk.Label(form, text="Especialidad", **label_style)
        espec_entry = tk.Entry(form, **entry_style)
        peso_label = tk.Label(form, text="Peso (kg)", **label_style)
        peso_entry = tk.Entry(form, **entry_style)
        altura_label = tk.Label(form, text="Altura (m)", **label_style)
        altura_entry = tk.Entry(form, **entry_style)

        tk.Label(form, text="Correo", **label_style).grid(row=10, column=0, pady=5, sticky="w")
        correo_entry = tk.Entry(form, **entry_style)
        correo_entry.grid(row=10, column=1, pady=5, sticky="ew")

        def actualizar_campos(*args):
            rol = rol_combo.get()
            # Generar ID automático
            if rol:
                prefix = {'admin': 'a', 'doctor': 'd', 'paciente': 'p'}[rol]
                existentes = [u['id'] for u in self.current_users if u['id'].startswith(prefix)]
                if existentes:
                    nums = [int(e[1:]) for e in existentes if e[1:].isdigit()]
                    next_id = max(nums) + 1 if nums else 1
                else:
                    next_id = 1
                id_var.set(f"{prefix}{next_id:03d}")
            # Ocultar todos los campos específicos
            espec_label.grid_remove()
            espec_entry.grid_remove()
            peso_label.grid_remove()
            peso_entry.grid_remove()
            altura_label.grid_remove()
            altura_entry.grid_remove()
            # Mostrar según rol
            if rol == 'doctor':
                espec_label.grid(row=7, column=0, pady=5, sticky="w")
                espec_entry.grid(row=7, column=1, pady=5, sticky="ew")
            elif rol == 'paciente':
                peso_label.grid(row=8, column=0, pady=5, sticky="w")
                peso_entry.grid(row=8, column=1, pady=5, sticky="ew")
                altura_label.grid(row=9, column=0, pady=5, sticky="w")
                altura_entry.grid(row=9, column=1, pady=5, sticky="ew")

        rol_combo.bind("<<ComboboxSelected>>", actualizar_campos)

        def save_user():
            rol = rol_combo.get()
            if not rol:
                messagebox.showerror("Error", "Selecciona un rol.")
                return
            new_user = {
                "id": id_var.get(),
                "usuario": usuario_entry.get(),
                "contrasena": pass_entry.get(),
                "rol": rol,
                "nombre": nombre_entry.get(),
                "documento": doc_entry.get(),
                "edad": edad_entry.get(),
                "correo": correo_entry.get()
            }
            if rol == 'doctor':
                new_user["especialidad"] = espec_entry.get()
            if rol == 'paciente':
                new_user["peso"] = peso_entry.get()
                new_user["altura"] = altura_entry.get()
            # Validaciones básicas
            campos_oblig = [new_user['usuario'], new_user['contrasena'], new_user['nombre'], new_user['documento'], new_user['edad'], new_user['correo']]
            if rol == 'doctor':
                campos_oblig.append(new_user['especialidad'])
            if rol == 'paciente':
                campos_oblig.extend([new_user['peso'], new_user['altura']])
            if not all(campos_oblig):
                messagebox.showerror("Error", "Todos los campos obligatorios deben estar completos.")
                return
            if any(u.get('usuario') == new_user['usuario'] for u in self.current_users):
                messagebox.showerror("Error", "El nombre de usuario ya existe.")
                return
            # Asegurar que todos los usuarios tengan los campos clave
            if 'usuario' not in new_user:
                new_user['usuario'] = usuario_entry.get()
            if 'contrasena' not in new_user:
                new_user['contrasena'] = pass_entry.get()
            self.current_users.append(new_user)
            self.save_users()
            self.refresh_users()
            create_window.destroy()
            messagebox.showinfo("Éxito", "Usuario creado correctamente")

        btn_style = {"font": ("Arial", 11, "bold"), "bg": "#b71c1c", "fg": "#fff", "activebackground": "#d32f2f", "activeforeground": "#fff", "relief": "flat", "height": 2}
        tk.Button(form, text="Guardar", command=save_user, **btn_style).grid(row=20, column=0, columnspan=2, pady=20, sticky="ew")

        form.columnconfigure(1, weight=1)

    def show_update_window(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Por favor seleccione un usuario para actualizar")
            return

        user_values = self.tree.item(selected[0])['values']
        user = next((u for u in self.current_users if u['id'] == user_values[0]), None)

        if not user:
            return

        update_window = tk.Toplevel(self.root)
        update_window.title("Actualizar Usuario")
        update_window.geometry("400x560")
        update_window.configure(bg="#fff")

        # Cabecera
        header = tk.Frame(update_window, bg="#b71c1c", height=90)
        header.pack(fill="x", side="top")
        try:
            from PIL import Image, ImageTk
            img = Image.open("gui/cabecera.png")
            img = img.resize((60, 60))
            header_img = ImageTk.PhotoImage(img)
            tk.Label(header, image=header_img, bg="#b71c1c").pack(pady=8)
            update_window.header_img = header_img
        except Exception:
            tk.Label(header, text="CLÍNICA ECG", font=("Arial", 16, "bold"), fg="#fff", bg="#b71c1c").pack(pady=16)

        tk.Label(update_window, text="Actualizar Usuario", font=("Arial", 14, "bold"), fg="#b71c1c", bg="#fff").pack(pady=(0, 8))

        form = tk.Frame(update_window, bg="#fff", padx=18, pady=10)
        form.pack(fill="both", expand=True)

        label_style = {"font": ("Arial", 10), "fg": "#b71c1c", "bg": "#fff"}
        entry_style = {"font": ("Arial", 11), "bg": "#fff", "fg": "#222", "relief": "solid", "bd": 1, "highlightthickness": 0, "insertbackground": "#222"}

        tk.Label(form, text="Rol", **label_style).grid(row=0, column=0, pady=5, sticky="w")
        rol_var = tk.StringVar(value=user.get('rol',''))
        rol_entry = tk.Entry(form, textvariable=rol_var, state="readonly", **entry_style)
        rol_entry.grid(row=0, column=1, pady=5, sticky="ew")

        tk.Label(form, text="ID", **label_style).grid(row=1, column=0, pady=5, sticky="w")
        id_var = tk.StringVar(value=user.get('id',''))
        id_entry = tk.Entry(form, textvariable=id_var, state="readonly", **entry_style)
        id_entry.grid(row=1, column=1, pady=5, sticky="ew")

        tk.Label(form, text="Usuario", **label_style).grid(row=2, column=0, pady=5, sticky="w")
        usuario_entry = tk.Entry(form, **entry_style)
        usuario_entry.insert(0, user.get('usuario',''))
        usuario_entry.grid(row=2, column=1, pady=5, sticky="ew")

        tk.Label(form, text="Contraseña", **label_style).grid(row=3, column=0, pady=5, sticky="w")
        pass_entry = tk.Entry(form, show="*", **entry_style)
        pass_entry.insert(0, user.get('contrasena',''))
        pass_entry.grid(row=3, column=1, pady=5, sticky="ew")

        tk.Label(form, text="Nombre", **label_style).grid(row=4, column=0, pady=5, sticky="w")
        nombre_entry = tk.Entry(form, **entry_style)
        nombre_entry.insert(0, user.get('nombre',''))
        nombre_entry.grid(row=4, column=1, pady=5, sticky="ew")

        tk.Label(form, text="Documento", **label_style).grid(row=5, column=0, pady=5, sticky="w")
        doc_entry = tk.Entry(form, **entry_style)
        doc_entry.insert(0, user.get('documento',''))
        doc_entry.grid(row=5, column=1, pady=5, sticky="ew")

        tk.Label(form, text="Edad", **label_style).grid(row=6, column=0, pady=5, sticky="w")
        edad_entry = tk.Entry(form, **entry_style)
        edad_entry.insert(0, user.get('edad',''))
        edad_entry.grid(row=6, column=1, pady=5, sticky="ew")

        # Campos específicos
        espec_label = tk.Label(form, text="Especialidad", **label_style)
        espec_entry = tk.Entry(form, **entry_style)
        peso_label = tk.Label(form, text="Peso (kg)", **label_style)
        peso_entry = tk.Entry(form, **entry_style)
        altura_label = tk.Label(form, text="Altura (m)", **label_style)
        altura_entry = tk.Entry(form, **entry_style)

        tk.Label(form, text="Correo", **label_style).grid(row=10, column=0, pady=5, sticky="w")
        correo_entry = tk.Entry(form, **entry_style)
        correo_entry.insert(0, user.get('correo',''))
        correo_entry.grid(row=10, column=1, pady=5, sticky="ew")

        # Mostrar campos según rol
        rol = user.get('rol','')
        if rol == 'doctor':
            espec_label.grid(row=7, column=0, pady=5, sticky="w")
            espec_entry.grid(row=7, column=1, pady=5, sticky="ew")
            espec_entry.insert(0, user.get('especialidad',''))
        elif rol == 'paciente':
            peso_label.grid(row=8, column=0, pady=5, sticky="w")
            peso_entry.grid(row=8, column=1, pady=5, sticky="ew")
            peso_entry.insert(0, user.get('peso',''))
            altura_label.grid(row=9, column=0, pady=5, sticky="w")
            altura_entry.grid(row=9, column=1, pady=5, sticky="ew")
            altura_entry.insert(0, user.get('altura',''))

        def update_user():
            user['usuario'] = usuario_entry.get()
            user['contrasena'] = pass_entry.get()
            user['nombre'] = nombre_entry.get()
            user['documento'] = doc_entry.get()
            user['edad'] = edad_entry.get()
            user['correo'] = correo_entry.get()
            if rol == 'doctor':
                user['especialidad'] = espec_entry.get()
            if rol == 'paciente':
                user['peso'] = peso_entry.get()
                user['altura'] = altura_entry.get()
            # Validaciones básicas
            campos_oblig = [user['usuario'], user['contrasena'], user['nombre'], user['documento'], user['edad'], user['correo']]
            if rol == 'doctor':
                campos_oblig.append(user['especialidad'])
            if rol == 'paciente':
                campos_oblig.extend([user['peso'], user['altura']])
            if not all(campos_oblig):
                messagebox.showerror("Error", "Todos los campos obligatorios deben estar completos.")
                return
            self.save_users()
            self.refresh_users()
            update_window.destroy()
            messagebox.showinfo("Éxito", "Usuario actualizado correctamente")

        btn_style = {"font": ("Arial", 11, "bold"), "bg": "#b71c1c", "fg": "#fff", "activebackground": "#d32f2f", "activeforeground": "#fff", "relief": "flat", "height": 2}
        tk.Button(form, text="Actualizar", command=update_user, **btn_style).grid(row=20, column=0, columnspan=2, pady=20, sticky="ew")

        form.columnconfigure(1, weight=1)

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Por favor seleccione un usuario para eliminar")
            return

        if not messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este usuario?"):
            return

        user_values = self.tree.item(selected[0])['values']
        self.current_users = [u for u in self.current_users if u['id'] != user_values[0]]
        self.save_users()
        self.refresh_users()
        messagebox.showinfo("Éxito", "Usuario eliminado correctamente")