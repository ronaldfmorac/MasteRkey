# 🛡️ MasteRkey - Gestor de Contraseñas Cifrado

MasteRkey es una aplicación de escritorio robusta diseñada para gestionar tus credenciales con la máxima seguridad. Utiliza cifrado **AES-256** para proteger tus datos y algoritmos de derivación de claves para asegurar que solo tú tengas acceso a tu bóvedpara asegurar que solo tú tengas acceso a tu bóveda.

## 📸 Vista Previa

#### 🔑 Configuración y Acceso
<p align="center">
  <img src="URL_DE_MASTERKEY1" width="45%" alt="Configuración inicial">
  <img src="URL_DE_MASTERKEY4" width="45%" alt="Pantalla de Login">
  <br>
  <em>Izquierda: Configuración de contraseña maestra inicial. Derecha: Interfaz de desbloqueo.</em>
</p>

#### 📂 Gestión de la Bóveda
<p align="center">
  <img src="URL_DE_MASTERKEY2" width="85%" alt="Añadir nueva cuenta">
  <br>
  <em>Formulario de registro con generador de contraseñas aleatorias integrado.</em>
</p>

<p align="center">
  <img src="URL_DE_MASTERKEY3" width="95%" alt="Panel principal">
  <br>
  <em>Panel principal con funciones de búsqueda, centrado de datos y acciones rápidas (Ver, Copiar, Editar, Borrar).</em>
</p>

---

## ✨ Características Principales
* **Cifrado de grado militar:** Protección de datos mediante Fernet (AES-256).
* **Interfaz Profesional:** Diseño oscuro (Dark Mode) optimizado con PyQt6.
* **Seguridad en Portapapeles:** Limpieza automática de contraseñas copiadas tras 30 segundos.
* **Exportación Segura:** Función para exportar tus registros a formato `.csv`.
* **Portabilidad:** Base de datos local SQLite cifrada (`vault.db`).

## 🚀 Guía de Compilación (.exe)

Para generar el ejecutable independiente en Windows:

### 1. Preparar el Entorno (Python 3.12)
```bash
python -m venv venv
.\venv\Scripts\activate
2. Instalar Dependencias
Bash
pip install -r requirements.txt
pip install pyinstaller
3. Comando de Compilación
Bash
pyinstaller --noconsole --onefile --name "MasteRkey" --icon="candado.ico" --hidden-import "pkgutil" --clean main.py
🛠️ Tecnologías Utilizadas
Lenguaje: Python 3.12

GUI: PyQt6

Criptografía: Cryptography / Bcrypt

Base de Datos: SQLite3