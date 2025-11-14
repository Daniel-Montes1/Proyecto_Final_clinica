❤️ Sistema de Gestión y Análisis de Electrocardiogramas (ECG)

Este proyecto es una aplicación completa desarrollada en Python para la gestión clínica de pacientes y el análisis básico de registros de electrocardiogramas (ECG).
Incluye un sistema gráfico (GUI) con roles separados para Administrador, Doctor y Paciente, permitiendo interacción segura y organizada con los datos clínicos.



🚀 Características principales


🔐 Sistema de Login

Acceso basado en credenciales almacenadas en usuarios.json.

Roles diferenciados: administrador, doctor y paciente.

Cada usuario tiene una interfaz adaptada a sus funciones.


👨‍⚕️ Panel del Doctor

Visualización y análisis de señales ECG.

Generación de gráficas mediante Matplotlib.

Registro de nuevos estudios ECG.

Carga y lectura de archivos CSV con señales crudas.

Exploración de descripciones clínicas desde descripcion_ecg.json.


👤 Panel del Paciente

Acceso a su historial de electrocardiogramas.

Visualización de gráficas simples de sus estudios previos.

Lectura de diagnósticos asociados.


🛠️ Panel del Administrador

Gestión de usuarios (crear, listar y eliminar).

Control general del sistema.


📁 Gestión de Datos

Los datos se almacenan de forma local en la carpeta data/:

registros_ecg.csv: registros cargados por los doctores.

usuarios.json: control de cuentas y roles.

descripcion_ecg.json: descripciones textuales de hallazgos comunes.


📊 Tecnologías utilizadas

Python 3.10+

Tkinter – Interfaz gráfica.

Matplotlib – Gráficas de ECG.

Pandas – Manejo de datos.

JSON / CSV – Almacenamiento local.
