"""
paciente_gui.py
-----------------------------------
Interfaz para el rol PACIENTE:
- Muestra la información del paciente (desde usuarios.json).
- Lista sus registros ECG (desde registros_ecg.csv).
- Permite visualizar la señal ECG seleccionada.
- Muestra las observaciones/interpretaciones médicas asociadas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json
import os

DATA_DIR = "data"
ECG_FILE = os.path.join(DATA_DIR, "registros_ecg.csv")
USERS_FILE = os.path.join(DATA_DIR, "usuarios.json")
DESC_FILE = os.path.join(DATA_DIR, "descripcion_ecg.json")


class PacienteWindow(tk.Toplevel):
    def __init__(self, root, usuario):
        super().__init__(root)
        self.title(f"Panel Paciente - {usuario}")
        self.geometry("1100x700")
        self.usuario = usuario

        self.configure(bg="#fff")
        # Cabecera gráfica
        header = tk.Frame(self, bg="#b71c1c", height=120)
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
        tk.Label(self, text="Panel de Paciente", font=("Arial", 16, "bold"), fg="#b71c1c", bg="#fff").pack(pady=(0, 8))

        # Layout principal
        main_frame = tk.Frame(self, bg="#fff", padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Layout principal: izquierda (info + lista), derecha (gráfica + descripción)
        left = tk.Frame(main_frame, width=340, bg="#f7f7f7")
        left.pack(side="left", fill="y", padx=10, pady=10)
        right = tk.Frame(main_frame, bg="#fff")
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ---- Left: info personal ----
        tk.Label(left, text="Datos del Paciente", font=("Arial", 11, "bold"), bg="#f7f7f7", fg="#b71c1c").pack(pady=8)
        self.text_info = tk.Text(left, height=10, width=38, font=("Arial", 10), bg="#fff", fg="#222", relief="solid", bd=1)
        self.text_info.pack(pady=4)

        tk.Label(left, text="Registros ECG:", bg="#f7f7f7", fg="#b71c1c", font=("Arial", 10, "bold")).pack(pady=6)
        self.listbox = tk.Listbox(left, height=14, width=45, font=("Arial", 10), bg="#fff", fg="#222", selectbackground="#b71c1c", selectforeground="#fff")
        self.listbox.pack(pady=4, fill="both", expand=True)
        self.listbox.bind("<Double-Button-1>", lambda e: self.mostrar_senal())

        btn_style = {"font": ("Arial", 11, "bold"), "bg": "#b71c1c", "fg": "#fff", "activebackground": "#d32f2f", "activeforeground": "#fff", "relief": "flat", "height": 2}
        tk.Button(left, text="Mostrar Señal", command=self.mostrar_senal, **btn_style).pack(pady=6, fill="x")
        tk.Button(left, text="Ver Observaciones", command=self.ver_observaciones, **btn_style).pack(pady=6, fill="x")
        tk.Button(left, text="Salir", command=self.destroy, **btn_style).pack(pady=6, fill="x")

        # ---- Right: gráfica ECG ----
        self.fig = Figure(figsize=(7, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Señal ECG")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Voltaje (mV)")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Área para observaciones
        tk.Label(right, text="Observaciones médicas:", font=("Arial", 10, "bold"), fg="#b71c1c", bg="#fff").pack(pady=5)
        # Mostrar observaciones del médico en modo solo lectura (el paciente no puede editar aquí)
        self.text_obs = tk.Text(right, height=4, font=("Arial", 10), bg="#fff", fg="#222", relief="solid", bd=1, state='disabled')
        self.text_obs.pack(fill="x", padx=10, pady=5)

        # Área para comentarios del paciente
        tk.Label(right, text="Tus comentarios/observaciones:", font=("Arial", 10, "bold"), fg="#b71c1c", bg="#fff").pack(pady=(10, 5))
        self.text_comentarios = tk.Text(right, height=6, font=("Arial", 10), bg="#fff", fg="#222", relief="solid", bd=1, wrap="word")
        self.text_comentarios.pack(fill="both", expand=True, padx=10, pady=5)

        # Botón para guardar comentarios
        tk.Button(right, text="Guardar mis comentarios", command=self.guardar_comentarios_paciente,
              font=("Arial", 10, "bold"), bg="#b71c1c", fg="#fff", activebackground="#d32f2f",
              activeforeground="#fff", relief="flat", height=2).pack(fill="x", padx=10, pady=5)

        # Estado interno
        self.current_records = []
        self.selected_record = None

        # Cargar info inicial del paciente
        self.cargar_informacion_paciente()

    # ------------------ Funciones de manejo de archivos ------------------
    def leer_json(self, path):
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def leer_registros_ecg(self):
        """Lee registros desde data/registros_ecg.csv y carga la señal desde el archivo indicado en 'archivo_senal'."""
        import csv

        if not os.path.exists(ECG_FILE):
            return []
        registros = []
        with open(ECG_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    record_id = row.get("id_registro") or row.get("id_registro".upper(), "")
                    # En registros.csv el documento del paciente está en 'documento_paciente'
                    patient_doc = row.get("documento_paciente") or row.get("documento", "")
                    timestamp = row.get("fecha", "")
                    sampling_rate = int(row.get("frecuencia_muestreo") or 250)
                    archivo_senal = row.get("archivo_senal") or row.get("archivo", "")
                    signal = []
                    ruta_senal = os.path.join(DATA_DIR, archivo_senal) if archivo_senal else ""
                    if ruta_senal and os.path.exists(ruta_senal):
                        with open(ruta_senal, "r", encoding="utf-8") as sf:
                            sreader = csv.DictReader(sf)
                            for srow in sreader:
                                try:
                                    signal.append(float(srow.get("voltaje_mV", srow.get("voltaje", 0))))
                                except Exception:
                                    continue
                    registros.append({
                        "record_id": record_id,
                        "patient_doc": patient_doc,
                        "timestamp": timestamp,
                        "sampling_rate": sampling_rate,
                        "num_samples": len(signal),
                        "signal": signal,
                        "archivo": archivo_senal
                    })
                except Exception:
                    continue
        return registros

    # ------------------ Funcionalidades principales ------------------
    def cargar_informacion_paciente(self):
        """Carga datos personales y ECG del paciente."""
        usuarios = self.leer_json(USERS_FILE)
        paciente = next((u for u in usuarios if u.get("usuario") == self.usuario or u.get("nombre") == self.usuario), None)

        self.text_info.delete("1.0", tk.END)
        if not paciente:
            self.text_info.insert(tk.END, "No se encontró información del paciente.")
            return

        doc = paciente.get("documento", "Desconocido")
        self.text_info.insert(tk.END, f"Nombre: {paciente.get('nombre', self.usuario)}\n")
        self.text_info.insert(tk.END, f"Documento: {doc}\n")
        self.text_info.insert(tk.END, f"Edad: {paciente.get('edad', 'N/A')}\n")
        self.text_info.insert(tk.END, f"Correo: {paciente.get('correo', 'N/A')}\n")

        peso = paciente.get("peso")
        altura = paciente.get("altura")
        if peso and altura:
            try:
                imc = float(peso) / (float(altura) ** 2)
                self.text_info.insert(tk.END, f"Peso: {peso} kg\nAltura: {altura} m\nIMC: {imc:.2f}\n")
            except Exception:
                self.text_info.insert(tk.END, "IMC: datos inválidos\n")

        # Mostrar ECGs
        registros = self.leer_registros_ecg()
        self.current_records = [r for r in registros if r["patient_doc"] == doc]
        self.current_records.sort(key=lambda x: x["timestamp"], reverse=True)

        self.listbox.delete(0, tk.END)
        if not self.current_records:
            self.listbox.insert(tk.END, "No hay registros ECG disponibles.")
            return

        for r in self.current_records:
            label = f"{r['record_id']} | {r['timestamp']} | {r['sampling_rate']}Hz | {r['num_samples']} muestras"
            self.listbox.insert(tk.END, label)

    def mostrar_senal(self):
        """Grafica la señal ECG seleccionada."""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un registro de la lista.")
            return
        idx = sel[0]
        if not self.current_records:
            return
        try:
            rec = self.current_records[idx]
        except IndexError:
            return

        self.selected_record = rec
        signal = rec.get("signal", [])
        sr = rec.get("sampling_rate", 250)

        if not signal:
            messagebox.showinfo("Información", "Este registro no contiene señal.")
            return

        # Crear eje de tiempo
        t = [i / sr for i in range(len(signal))]

        # Graficar
        self.ax.clear()
        self.ax.plot(t, signal, color="red")
        self.ax.set_title(f"ECG {rec['record_id']} - {rec['timestamp']}")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Voltaje (mV)")
        self.ax.grid(True)
        self.canvas.draw()

    def ver_observaciones(self):
        """Muestra las observaciones clínicas del registro seleccionado."""
        if not self.selected_record:
            messagebox.showwarning("Aviso", "Selecciona primero un registro para ver las observaciones.")
            return

        rec_id = self.selected_record["record_id"]
        descs = self.leer_json(DESC_FILE)
        asociadas = []
        for d in descs:
            # soportar distintos esquemas: 'record_id' o 'id_registro'
            if d.get("record_id") == rec_id or d.get("id_registro") == rec_id or d.get("id_registro", "").lower() == rec_id.lower():
                asociadas.append(d)

        # Activar temporalmente el widget para actualizar su contenido, luego volver a deshabilitar
        self.text_obs.config(state='normal')
        self.text_obs.delete("1.0", tk.END)
        if not asociadas:
            self.text_obs.insert(tk.END, "No hay observaciones para este registro.")
            self.text_obs.config(state='disabled')
            return

        for d in asociadas:
            # obtener autor/fecha/texto según esquema
            autor = d.get("author") or d.get("autor", "Desconocido")
            fecha = d.get("timestamp") or d.get("fecha_registro", "")
            # texto puede estar en distintas claves
            texto = d.get("text") or d.get("diagnostico_automatico") or d.get("observaciones_medico") or ""
            self.text_obs.insert(tk.END, f"[{fecha}] {autor}:\n{texto}\n\n")

    def guardar_comentarios_paciente(self):
        """Guarda los comentarios del paciente en un archivo JSON."""
        if not self.selected_record:
            messagebox.showwarning("Aviso", "Selecciona primero un registro para agregar comentarios.")
            return

        comentario = self.text_comentarios.get("1.0", tk.END).strip()
        if not comentario:
            messagebox.showwarning("Aviso", "Por favor escribe algún comentario antes de guardar.")
            return

        from datetime import datetime
        
        comentarios_file = os.path.join(DATA_DIR, "comentarios_paciente.json")
        comentarios = self.leer_json(comentarios_file)
        nuevo = {
            "id": f"c{int(datetime.utcnow().timestamp())}",
            "paciente": self.usuario,
            "record_id": self.selected_record["record_id"],
            "patient_doc": self.selected_record.get("patient_doc", ""),
            "timestamp": datetime.utcnow().isoformat(),
            "comentario": comentario
        }
        comentarios.append(nuevo)
        self.guardar_json(comentarios_file, comentarios)
        messagebox.showinfo("Éxito", "Comentario guardado correctamente.")
        self.text_comentarios.delete("1.0", tk.END)

    def guardar_json(self, path, data):
        """Guarda data en un archivo JSON."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Dejar el widget en modo solo lectura para el paciente
        self.text_obs.config(state='disabled')
