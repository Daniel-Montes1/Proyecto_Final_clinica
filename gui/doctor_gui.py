"""
doctor_gui.py
-----------------------------------
Interfaz para el rol DOCTOR:
- Buscar paciente por documento (patient_doc).
- Calcular IMC si el paciente tiene 'peso' y 'altura' en usuarios.json.
- Listar registros ECG del paciente (desde data/registros_ecg.csv).
- Mostrar la señal seleccionada (graficada).
- Agregar una descripción/interpretación y guardarla en data/descripcion_ecg.json.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json
import os
from datetime import datetime

DATA_DIR = "data"
ECG_FILE = os.path.join(DATA_DIR, "registros_ecg.csv")
USERS_FILE = os.path.join(DATA_DIR, "usuarios.json")
DESC_FILE = os.path.join(DATA_DIR, "descripcion_ecg.json")


class DoctorWindow(tk.Toplevel):
    def __init__(self, root, usuario):
        super().__init__(root)
        self.title(f"Panel Doctor - {usuario}")
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
        tk.Label(self, text="Panel de Doctor", font=("Arial", 16, "bold"), fg="#b71c1c", bg="#fff").pack(pady=(0, 8))

        # Layout principal
        main_frame = tk.Frame(self, bg="#fff", padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Layout: izquierda para búsqueda / lista, derecha para gráfica / acciones
        left = tk.Frame(main_frame, width=340, bg="#f7f7f7")
        left.pack(side="left", fill="y", padx=10, pady=10)
        left.pack_propagate(False)
        right = tk.Frame(main_frame, bg="#fff")
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ---- Left: búsqueda y lista ----
        tk.Label(left, text="Buscar paciente por documento", font=("Arial", 11, "bold"), bg="#f7f7f7", fg="#b71c1c").pack(pady=8)
        self.entry_doc = tk.Entry(left, font=("Arial", 12), bg="#fff", fg="#222", relief="solid", bd=1, highlightthickness=0, insertbackground="#222")
        self.entry_doc.pack(pady=6, fill="x")

        tk.Button(left, text="Ver Historial ECG", command=self.buscar_historial, font=("Arial", 11, "bold"), bg="#b71c1c", fg="#fff", activebackground="#d32f2f", activeforeground="#fff", relief="flat", height=2).pack(pady=6, fill="x")

        # IMC y datos del paciente
        self.info_text = tk.Text(left, height=8, width=36, font=("Arial", 10), bg="#fff", fg="#222", relief="solid", bd=1)
        self.info_text.pack(pady=6)

        tk.Label(left, text="Registros ECG del paciente:", bg="#f7f7f7", fg="#b71c1c", font=("Arial", 10, "bold")).pack(pady=6)
        self.listbox = tk.Listbox(left, height=12, width=45, font=("Arial", 10), bg="#fff", fg="#222", selectbackground="#b71c1c", selectforeground="#fff")
        self.listbox.pack(pady=4, fill="both", expand=True)
        self.listbox.bind("<Double-Button-1>", lambda e: self.mostrar_senal())

        # Frame para botones de acción (siempre visible abajo)
        btns_frame = tk.Frame(left, bg="#f7f7f7")
        btns_frame.pack(side="bottom", fill="x", pady=(8, 0))
        btn_style = {"font": ("Arial", 11, "bold"), "bg": "#b71c1c", "fg": "#fff", "activebackground": "#d32f2f", "activeforeground": "#fff", "relief": "flat", "height": 2}
        tk.Button(btns_frame, text="Mostrar Señal", command=self.mostrar_senal, **btn_style).pack(fill="x", pady=2)
        tk.Button(btns_frame, text="Generar / Guardar Descripción", command=self.generar_descripcion, **btn_style).pack(fill="x", pady=2)
        tk.Button(btns_frame, text="Salir", command=self.destroy, **btn_style).pack(fill="x", pady=2)

        # ---- Right: gráfica ----
        self.fig = Figure(figsize=(7,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Señal ECG")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Voltaje (mV)")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # state
        self.current_records = []  # lista de dicts de registros del paciente
        self.selected_record = None

    # ------------------ Helpers de archivo -------------------------
    def leer_json(self, path):
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def guardar_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

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
                    patient_doc = row.get("documento_paciente") or row.get("documento", "")
                    timestamp = row.get("fecha", "")
                    sampling_rate = int(row.get("frecuencia_muestreo") or 250)
                    archivo_senal = row.get("archivo_senal") or row.get("archivo", "")
                    # Cargar señal desde archivo CSV referido (tiempo_s, voltaje_mV)
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

    # ------------------ Funcionalidades ---------------------------
    def buscar_historial(self):
        doc = self.entry_doc.get().strip()
        if not doc:
            messagebox.showwarning("Aviso", "Ingresa el número de documento del paciente.")
            return

        # Cargar usuarios y buscar info del paciente
        usuarios = self.leer_json(USERS_FILE)
        paciente_info = next((u for u in usuarios if u.get("documento") == doc or u.get("usuario") == doc or u.get("id") == doc), None)

        self.info_text.delete("1.0", tk.END)
        if paciente_info:
            nombre = paciente_info.get("nombre", paciente_info.get("usuario", "Sin nombre"))
            self.info_text.insert(tk.END, f"Nombre: {nombre}\n")
            self.info_text.insert(tk.END, f"Documento: {doc}\n")
            # IMC si existen peso (kg) y altura (m)
            peso = paciente_info.get("peso")
            altura = paciente_info.get("altura")
            if peso and altura:
                try:
                    imc = float(peso) / (float(altura) ** 2)
                    self.info_text.insert(tk.END, f"Peso: {peso} kg\nAltura: {altura} m\nIMC: {imc:.2f}\n")
                except Exception:
                    self.info_text.insert(tk.END, "IMC: datos inválidos\n")
            else:
                self.info_text.insert(tk.END, "IMC: datos no disponibles (campo 'peso' o 'altura')\n")
        else:
            self.info_text.insert(tk.END, "Paciente no encontrado en usuarios.json\n")

        # Cargar registros ECG y filtrar por patient_doc
        regs = self.leer_registros_ecg()
        paciente_regs = [r for r in regs if r["patient_doc"] == doc]
        paciente_regs.sort(key=lambda x: x["timestamp"], reverse=True)

        self.current_records = paciente_regs
        self.listbox.delete(0, tk.END)
        if not paciente_regs:
            self.listbox.insert(tk.END, "No hay registros ECG para este paciente.")
            return

        for r in paciente_regs:
            label = f"{r['record_id']} | {r['timestamp']} | {r['sampling_rate']}Hz | {r['num_samples']} muestras"
            self.listbox.insert(tk.END, label)

    def mostrar_senal(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un registro de la lista.")
            return
        idx = sel[0]
        if not self.current_records:
            messagebox.showwarning("Aviso", "No hay registros cargados.")
            return
        try:
            rec = self.current_records[idx]
        except IndexError:
            messagebox.showerror("Error", "Selección inválida.")
            return

        self.selected_record = rec
        signal = rec.get("signal", [])
        sr = rec.get("sampling_rate", 250)

        if not signal:
            messagebox.showinfo("Información", "El registro no contiene señal o está vacía.")
            return

        # preparar tiempo en segundos
        t = [i / sr for i in range(len(signal))]

        # dibujar
        self.ax.clear()
        self.ax.plot(t, signal)
        self.ax.set_title(f"ECG {rec['record_id']} - {rec['timestamp']}")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Voltaje (mV)")
        self.ax.grid(True)
        self.canvas.draw()

    def generar_descripcion(self):
        if not self.selected_record:
            messagebox.showwarning("Aviso", "Muestra primero una señal o selecciona un registro.")
            return

        rec = self.selected_record
        # Crear ventana modal grande para la interpretación
        ventana = tk.Toplevel(self)
        ventana.title("Interpretación Clínica ECG")
        ventana.geometry("800x500")
        ventana.configure(bg="#fff")
        ventana.resizable(True, True)
        ventana.grab_set()  # Modal

        # Cabecera
        header = tk.Frame(ventana, bg="#b71c1c", height=50)
        header.pack(fill="x", side="top")
        tk.Label(header, text="Ingresa la Descripción/Interpretación Clínica", 
                 font=("Arial", 14, "bold"), fg="#fff", bg="#b71c1c").pack(pady=10)

        # Información del registro
        info_frame = tk.Frame(ventana, bg="#f7f7f7", padx=10, pady=8)
        info_frame.pack(fill="x")
        info_text = f"Registro: {rec['record_id']} | Paciente: {rec['patient_doc']} | {rec['timestamp']}"
        tk.Label(info_frame, text=info_text, font=("Arial", 10), bg="#f7f7f7", fg="#555").pack(anchor="w")

        # Área de texto grande
        text_frame = tk.Frame(ventana, bg="#fff", padx=10, pady=10)
        text_frame.pack(fill="both", expand=True)
        
        tk.Label(text_frame, text="Observaciones:", font=("Arial", 11, "bold"), bg="#fff", fg="#b71c1c").pack(anchor="w", pady=(0, 5))
        
        text_widget = tk.Text(text_frame, height=15, width=90, font=("Arial", 11), 
                              bg="#fff", fg="#222", relief="solid", bd=1, wrap="word")
        text_widget.pack(fill="both", expand=True, side="left")

        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y", padx=(5, 0))
        text_widget.config(yscrollcommand=scrollbar.set)

        # Botones
        btn_frame = tk.Frame(ventana, bg="#f7f7f7", padx=10, pady=10)
        btn_frame.pack(fill="x", side="bottom")

        def guardar_interpretacion():
            texto = text_widget.get("1.0", tk.END).strip()
            if not texto:
                messagebox.showwarning("Aviso", "Por favor, ingresa una descripción.")
                return
            
            # Cargar descripciones previas
            descs = self.leer_json(DESC_FILE)
            nueva = {
                "obs_id": f"o{int(datetime.utcnow().timestamp())}",
                "record_id": rec["record_id"],
                "patient_doc": rec["patient_doc"],
                "timestamp": datetime.utcnow().isoformat(),
                "author": self.usuario,
                "text": texto
            }
            descs.append(nueva)
            self.guardar_json(DESC_FILE, descs)
            messagebox.showinfo("Guardado", "Descripción guardada correctamente en descripcion_ecg.json")
            ventana.destroy()

        def cancelar():
            ventana.destroy()

        btn_style = {"font": ("Arial", 11, "bold"), "bg": "#b71c1c", "fg": "#fff", 
                     "activebackground": "#d32f2f", "activeforeground": "#fff", "relief": "flat", "height": 2}
        
        tk.Button(btn_frame, text="Guardar Descripción", command=guardar_interpretacion, 
                  width=20, **btn_style).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", command=cancelar, 
                  width=20, bg="#999", activebackground="#bbb", **{k: v for k, v in btn_style.items() if k != "bg"}).pack(side="left", padx=5)

