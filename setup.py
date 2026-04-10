import sys
from cx_Freeze import setup, Executable

# Dependencias adicionales
build_exe_options = {
    "packages": ["os", "sys", "bcrypt", "cryptography", "PyQt6"],
    "includes": ["pkgutil"], # Forzamos el que dio error antes
    "include_files": ["candado.ico"], # Incluimos tu icono
}

base = None
if sys.platform == "win32":
    base = "gui"  # Antes era Win32GUI, ahora cx_Freeze pide 'gui' para versiones nuevas

setup(
    name="MasteRkey",
    version="1.0",
    description="Gestor de Contraseñas Seguro",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="MasteRkey.exe",
            icon="candado.ico"
        )
    ],
)