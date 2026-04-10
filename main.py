import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, QEvent, QTimer
import database
import gui

# Tema visual CSS (QSS) - Tonos Azules Profesionales
STYLE_SHEET = """
QWidget {
    background-color: #0b192c;
    color: #e2e8f0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QPushButton {
    background-color: #1e3a8a;
    border: 1px solid #3b82f6;
    border-radius: 5px;
    padding: 6px 12px;
    color: white;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #2563eb;
}
QPushButton:pressed {
    background-color: #1d4ed8;
}
QLineEdit {
    background-color: #1e293b;
    border: 1px solid #475569;
    border-radius: 4px;
    padding: 6px;
    color: white;
}
QLineEdit:focus {
    border: 1px solid #3b82f6;
}
QTableWidget {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 5px;
    gridline-color: #1e293b;
}
QTableWidget::item {
    padding: 5px;
    border-bottom: 1px solid #1e293b;
}
QHeaderView::section {
    background-color: #1e3a8a;
    color: white;
    padding: 6px;
    border: none;
    border-right: 1px solid #0f172a;
    font-weight: bold;
}
QMessageBox {
    background-color: #0f172a;
}
"""

class AppController(QObject):
    """
    Controlador principal.
    Maneja el flujo Login -> Ventana Principal y el Timeout de Inactividad Global.
    """
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.main_window = None
        self.key = None
        
        # Temporizador de Inactividad (15 Minutos = 900,000 ms)
        self.timeout_ms = 15 * 60 * 1000 
        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.lock_application)
        
        # Instalar un filtro de eventos global para detectar actividad
        self.app.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Intercepta eventos de teclado o ratón para resetear el temporizador de cierre."""
        if event.type() in (QEvent.Type.KeyPress, QEvent.Type.MouseMove, QEvent.Type.MouseButtonPress):
            if self.key is not None:  # Solo reiniciar si está desbloqueado
                self.idle_timer.start(self.timeout_ms)
        return False

    def start(self):
        """Inicia el ciclo de la app."""
        database.init_db()
        self.show_login()

    def show_login(self):
        """Muestra la ventana de login."""
        login = gui.LoginDialog()
        if login.exec():
            self.key = login.key
            self.open_main_window()
        else:
            sys.exit(0)

    def open_main_window(self):
        """Abre la bóveda."""
        self.main_window = gui.MainWindow(self.key)
        self.main_window.show()
        self.idle_timer.start(self.timeout_ms)

    def lock_application(self):
        """Cierra la bóveda y borra la clave de memoria por inactividad."""
        self.idle_timer.stop()
        self.key = None # Destruye la clave maestra de memoria
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        
        # Aviso y vuelta al login
        import PyQt6.QtWidgets as QtWidgets
        msg = QtWidgets.QMessageBox()
        msg.warning(None, "Bloqueo Automático", "La sesión se ha cerrado por inactividad (15 min).")
        self.show_login()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    
    controller = AppController(app)
    controller.start()
    
    sys.exit(app.exec())