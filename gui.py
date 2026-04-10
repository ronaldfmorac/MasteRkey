import csv
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
                             QApplication, QAbstractItemView, QProgressBar, QCheckBox, QFileDialog)
from PyQt6.QtCore import Qt, QTimer, QSize # <-- AÑADIDO QSize
from PyQt6.QtGui import QIcon, QFont, QAction # <-- AÑADIDO QAction si no estaba

import security
import database

class LoginDialog(QDialog):
    """Ventana de Login y Configuración Inicial"""
    def __init__(self):
        super().__init__()
        self.key = None # Aquí guardaremos la clave derivada temporalmente
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("MasteRkey - Login")
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        title = QLabel("MasteRkey Password Manager")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #60a5fa;")
        layout.addWidget(title)
        
        self.is_setup = database.is_first_run()
        
        if self.is_setup:
            lbl = QLabel("Bienvenido. Configura tu Contraseña Maestra:")
            lbl.setStyleSheet("color: #94a3b8;")
            layout.addWidget(lbl)
            
            self.pwd_input = QLineEdit()
            self.pwd_input.setPlaceholderText("Nueva Contraseña Maestra")
            self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addWidget(self.pwd_input)
            
            self.pwd_confirm = QLineEdit()
            self.pwd_confirm.setPlaceholderText("Confirmar Contraseña")
            self.pwd_confirm.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addWidget(self.pwd_confirm)
            
            btn = QPushButton("Crear y Entrar")
            btn.clicked.connect(self.handle_setup)
            layout.addWidget(btn)
        else:
            lbl = QLabel("Introduce tu Contraseña Maestra:")
            lbl.setStyleSheet("color: #94a3b8;")
            layout.addWidget(lbl)
            
            self.pwd_input = QLineEdit()
            self.pwd_input.setPlaceholderText("Contraseña Maestra")
            self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.pwd_input.returnPressed.connect(self.handle_login)
            layout.addWidget(self.pwd_input)
            
            btn = QPushButton("Desbloquear")
            btn.clicked.connect(self.handle_login)
            layout.addWidget(btn)
            
        self.setLayout(layout)

    def handle_setup(self):
        pwd = self.pwd_input.text()
        conf = self.pwd_confirm.text()
        
        if len(pwd) < 8:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 8 caracteres.")
            return
        if pwd != conf:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            return
            
        # Generar hash y salt
        hashed = security.hash_master_password(pwd)
        salt = security.generate_salt()
        database.setup_master_password(hashed, salt)
        
        # Derivar clave para la sesión
        self.key = security.derive_key(pwd, salt)
        self.accept()

    def handle_login(self):
        pwd = self.pwd_input.text()
        data = database.get_master_data()
        if not data:
            QMessageBox.critical(self, "Error Fatal", "Base de datos corrupta.")
            return
            
        stored_hash, salt = data
        if security.verify_master_password(pwd, stored_hash):
            self.key = security.derive_key(pwd, salt)
            self.accept()
        else:
            QMessageBox.warning(self, "Denegado", "Contraseña maestra incorrecta.")
            self.pwd_input.clear()

class EntryDialog(QDialog):
    """Ventana para Agregar/Editar Contraseñas"""
    def __init__(self, entry_id=None, service="", username="", password=""):
        super().__init__()
        self.entry_id = entry_id
        self.service = service
        self.username = username
        self.password = password
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Editar Cuenta" if self.entry_id else "Nueva Cuenta")
        self.setFixedSize(400, 450)
        
        layout = QVBoxLayout()
        
        # Servicio
        layout.addWidget(QLabel("Servicio / Sitio Web:"))
        self.in_service = QLineEdit(self.service)
        layout.addWidget(self.in_service)
        
        # Usuario
        layout.addWidget(QLabel("Nombre de Usuario / Email:"))
        self.in_username = QLineEdit(self.username)
        layout.addWidget(self.in_username)
        
        # Contraseña
        layout.addWidget(QLabel("Contraseña:"))
        pwd_layout = QHBoxLayout()
        self.in_password = QLineEdit(self.password)
        self.in_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.in_password.textChanged.connect(self.update_strength)
        pwd_layout.addWidget(self.in_password)
        
        btn_view = QPushButton("👁")
        btn_view.setFixedWidth(40)
        btn_view.pressed.connect(lambda: self.in_password.setEchoMode(QLineEdit.EchoMode.Normal))
        btn_view.released.connect(lambda: self.in_password.setEchoMode(QLineEdit.EchoMode.Password))
        pwd_layout.addWidget(btn_view)
        
        layout.addLayout(pwd_layout)
        
        # Indicador de fuerza
        self.lbl_strength = QLabel("Fuerza: -")
        self.lbl_strength.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(self.lbl_strength)
        
        # Generador de contraseñas integrado
        gen_box = QVBoxLayout()
        gen_box.addWidget(QLabel("Generar Contraseña Segura:"))
        
        chk_layout = QHBoxLayout()
        self.chk_upper = QCheckBox("A-Z")
        self.chk_upper.setChecked(True)
        self.chk_lower = QCheckBox("a-z")
        self.chk_lower.setChecked(True)
        self.chk_nums = QCheckBox("0-9")
        self.chk_nums.setChecked(True)
        self.chk_sym = QCheckBox("!@#")
        self.chk_sym.setChecked(True)
        
        chk_layout.addWidget(self.chk_upper)
        chk_layout.addWidget(self.chk_lower)
        chk_layout.addWidget(self.chk_nums)
        chk_layout.addWidget(self.chk_sym)
        gen_box.addLayout(chk_layout)
        
        btn_gen = QPushButton("Generar y Aplicar")
        btn_gen.setStyleSheet("background-color: #334155; border: 1px solid #475569;")
        btn_gen.clicked.connect(self.generate_pwd)
        gen_box.addWidget(btn_gen)
        
        layout.addLayout(gen_box)
        layout.addStretch()
        
        # Botones de Acción
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet("background-color: #334155;")
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        if self.password:
            self.update_strength()

    def generate_pwd(self):
        pwd = security.generate_secure_password(
            length=16,
            use_upper=self.chk_upper.isChecked(),
            use_lower=self.chk_lower.isChecked(),
            use_numbers=self.chk_nums.isChecked(),
            use_symbols=self.chk_sym.isChecked()
        )
        self.in_password.setText(pwd)
        
    def update_strength(self):
        pwd = self.in_password.text()
        strength = security.check_password_strength(pwd)
        color = "#ef4444" if strength == "Débil" else "#eab308" if strength == "Media" else "#22c55e"
        self.lbl_strength.setText(f"Fuerza: {strength}")
        self.lbl_strength.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold;")
        
    def get_data(self):
        return self.in_service.text(), self.in_username.text(), self.in_password.text()


class MainWindow(QMainWindow):
    """Panel Principal de Gestión de Contraseñas"""
    def __init__(self, key: bytes):
        super().__init__()
        self.key = key  # Clave AES-256 en memoria mientras esté abierta
        self.entries = [] # Datos descifrados temporalmente en memoria
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("MasteRkey - Bóveda Cifrada")
        self.setMinimumSize(850, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Barra superior (Toolbar)
        top_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar servicio o usuario...")
        self.search_input.textChanged.connect(self.filter_table)
        top_layout.addWidget(self.search_input)
        
        # Botón Exportar corregido
        self.btn_export = QPushButton(" 📤 Exportar CSV")
        self.btn_export.setFixedWidth(130)
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #4b5563;
                color: white;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #6b7280; }
        """)
        self.btn_export.clicked.connect(self.export_to_csv)
        top_layout.addWidget(self.btn_export)
        
        # Botón Agregar
        btn_add = QPushButton("➕ Agregar Nueva")
        btn_add.setFixedWidth(150)
        btn_add.clicked.connect(self.add_entry)
        top_layout.addWidget(btn_add)
        
        main_layout.addLayout(top_layout)
        
        # Tabla de Contraseñas
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Servicio", "Usuario", "Contraseña", "Acciones"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 160)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 320)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        
        main_layout.addWidget(self.table)
        
    def load_data(self):
        self.table.setRowCount(0)
        self.entries.clear()
        
        raw_rows = database.get_all_entries()
        for row in raw_rows:
            db_id, enc_service, enc_user, enc_pwd = row
            # Descifrado al vuelo para mostrar (Solo memoria)
            service = security.decrypt_data(self.key, enc_service)
            username = security.decrypt_data(self.key, enc_user)
            password = security.decrypt_data(self.key, enc_pwd)
            
            if service and password: # Verifica que el descifrado fue exitoso
                self.entries.append({
                    'id': db_id,
                    'service': service,
                    'username': username,
                    'password': password
                })
                
        self.populate_table(self.entries)

    def populate_table(self, data):
        self.table.setRowCount(0)
        # Ajustar la altura de las filas para que los botones quepan bien
        self.table.verticalHeader().setDefaultSectionSize(40) 

        for i, entry in enumerate(data):
            self.table.insertRow(i)
            # 1. Celda de Servicio
            item_service = QTableWidgetItem(entry['service'])
            item_service.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # CENTRADO
            self.table.setItem(i, 0, item_service)
            
            # 2. Celda de Usuario
            item_user = QTableWidgetItem(entry['username'])
            item_user.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # CENTRADO
            self.table.setItem(i, 1, item_user)
            
            # 3. Celda de Contraseña (Puntos)
            item_pass = QTableWidgetItem("••••••••")
            item_pass.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # CENTRADO
            self.table.setItem(i, 2, item_pass)
            
            # Widget contenedor de Acciones
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2) # Márgenes mínimos
            action_layout.setSpacing(4) # Espacio entre botones
            
            # --- ESTILOS VISUALES PARA LOS BOTONES ---
            # Usamos emojis Unicode como iconos para compatibilidad total
            
            # 1. Botón Ver (Ojo 👁️)
            btn_view = QPushButton(" 👁️ Ver")
            btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_view.setToolTip("Mantener presionado para ver la contraseña")
            # Estilo específico: Azul claro para diferenciar
            btn_view.setStyleSheet("""
                QPushButton {
                    background-color: #0369a1; /* Azul cyan oscuro */
                    border: 1px solid #0ea5e9;
                    padding: 4px 8px;
                    font-size: 11px;
                }
                QPushButton:hover { background-color: #0ea5e9; }
                QPushButton:pressed { background-color: #0c4a6e; }
            """)
            btn_view.pressed.connect(lambda i=i, p=entry['password']: self.table.item(i, 2).setText(p))
            btn_view.released.connect(lambda i=i: self.table.item(i, 2).setText("••••••••"))
            
            # 2. Botón Copiar (Portapapeles 📋)
            btn_copy = QPushButton(" 📋 Copiar")
            btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_copy.setToolTip("Copiar contraseña de forma segura")
            # Estilo específico: Verde para indicar éxito/acción positiva
            btn_copy.setStyleSheet("""
                QPushButton {
                    background-color: #15803d; /* Verde oscuro */
                    border: 1px solid #22c55e;
                    padding: 4px 8px;
                    font-size: 11px;
                }
                QPushButton:hover { background-color: #16a34a; }
                QPushButton:pressed { background-color: #14532d; }
            """)
            btn_copy.clicked.connect(lambda _, p=entry['password']: self.secure_copy(p))
            
            # 3. Botón Editar (Lápiz ✏️)
            btn_edit = QPushButton(" ✏️ Editar")
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setToolTip("Modificar los datos de esta cuenta")
            # Estilo específico: Naranja/Amarillo para precaución/cambio
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #a16207; /* Amarillo/Naranja oscuro */
                    border: 1px solid #eab308;
                    padding: 4px 8px;
                    font-size: 11px;
                }
                QPushButton:hover { background-color: #ca8a04; }
                QPushButton:pressed { background-color: #713f12; }
            """)
            btn_edit.clicked.connect(lambda _, e=entry: self.edit_entry(e))
            
            # 4. Botón Borrar (Papelera 🗑️)
            btn_del = QPushButton(" 🗑️ Borrar")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setToolTip("Eliminar esta cuenta permanentemente")
            # Estilo específico: Rojo intenso para peligro
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #b91c1c; /* Rojo oscuro */
                    border: 1px solid #ef4444;
                    padding: 4px 8px;
                    font-size: 11px;
                }
                QPushButton:hover { background-color: #dc2626; }
                QPushButton:pressed { background-color: #7f1d1d; }
            """)
            btn_del.clicked.connect(lambda _, e_id=entry['id']: self.delete_entry(e_id))
            
            # Añadir botones al layout
            action_layout.addWidget(btn_view)
            action_layout.addWidget(btn_copy)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_del)
            
            # Poner el widget contenedor en la celda de acciones
            self.table.setCellWidget(i, 3, action_widget)

    def filter_table(self, text):
        filtered = [e for e in self.entries if text.lower() in e['service'].lower() or text.lower() in e['username'].lower()]
        self.populate_table(filtered)

    def secure_copy(self, text):
        cb = QApplication.clipboard()
        cb.setText(text)
        QMessageBox.information(self, "Copiado", "Contraseña en el portapapeles.\nSe borrará de forma segura en 30 segundos.")
        
        # Limpiar portapapeles después de 30 segundos si coincide con lo que copiamos
        QTimer.singleShot(30000, lambda: cb.clear() if cb.text() == text else None)

    def add_entry(self):
        dialog = EntryDialog()
        if dialog.exec():
            srv, usr, pwd = dialog.get_data()
            if not srv or not pwd:
                QMessageBox.warning(self, "Error", "Servicio y Contraseña son obligatorios.")
                return
                
            enc_srv = security.encrypt_data(self.key, srv)
            enc_usr = security.encrypt_data(self.key, usr)
            enc_pwd = security.encrypt_data(self.key, pwd)
            
            database.add_entry(enc_srv, enc_usr, enc_pwd)
            self.load_data()

    def edit_entry(self, entry):
        dialog = EntryDialog(entry['id'], entry['service'], entry['username'], entry['password'])
        if dialog.exec():
            srv, usr, pwd = dialog.get_data()
            enc_srv = security.encrypt_data(self.key, srv)
            enc_usr = security.encrypt_data(self.key, usr)
            enc_pwd = security.encrypt_data(self.key, pwd)
            
            database.update_entry(entry['id'], enc_srv, enc_usr, enc_pwd)
            self.load_data()

    def delete_entry(self, entry_id):
        reply = QMessageBox.question(self, 'Confirmar', '¿Borrar esta contraseña de forma permanente?', 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_entry(entry_id)
            self.load_data()
            
    def closeEvent(self, event):
        # Limpiar clave de memoria al cerrar
        self.key = b"\x00" * 32
        self.entries.clear()
        super().closeEvent(event)
    
    def export_to_csv(self):
        if not self.entries:
            QMessageBox.warning(self, "Sin datos", "No hay contraseñas para exportar.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Contraseñas", "MasteRkey_backup.csv", "CSV Files (*.csv)"
        )
    
        if path:
            try:
                with open(path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    # Escribir encabezados
                    writer.writerow(["Servicio", "Usuario", "Contraseña"])
                    
                    # Escribir los datos desde la memoria (ya descifrados)
                    for entry in self.entries:
                        writer.writerow([entry['service'], entry['username'], entry['password']])
                
                QMessageBox.information(self, "Éxito", f"Datos exportados correctamente en:\n{path}\n\n¡RECUERDA: El archivo no está cifrado!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar: {str(e)}")