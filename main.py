"""
Punto de entrada principal del sistema ECG Clínica del Corazón.

Desde aquí se lanza la interfaz de inicio de sesión, que redirige
a las interfaces correspondientes según el rol del usuario:
Administrador, Doctor o Paciente.
"""

import tkinter as tk
from gui.login import LoginWindow

def main():
    root = tk.Tk()
    root.title("Clínica del Corazón ❤️‍🩹")
    root.geometry("500x400")
    root.resizable(False, False)

    app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()