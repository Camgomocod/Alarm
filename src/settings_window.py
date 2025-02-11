from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtGui import QFont

class AlarmSettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Alarma")
        # Asegurar que la ventana sea modal y esté al frente
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QDialog { 
                background-color: #000000;
                min-width: 400px;
                min-height: 300px;
            }
            QLabel { 
                color: #00ff00; 
                font-size: 32px; 
                font-family: 'Digital-7';
            }
            QPushButton { 
                background-color: #003300; 
                color: #00ff00; 
                border: 2px solid #00ff00;
                border-radius: 15px;
                min-height: 60px;
                min-width: 150px;
                font-size: 24px;
                font-family: 'Digital-7';
            }
            QPushButton:hover {
                background-color: #004400;
            }
            QSpinBox { 
                background-color: #003300; 
                color: #00ff00; 
                border: 2px solid #00ff00;
                border-radius: 10px;
                min-height: 60px;
                min-width: 100px;
                font-size: 36px;
                font-family: 'Digital-7';
            }
        """)
        
        layout = QVBoxLayout()
        
        # Agregar título visible
        title_label = QLabel("Configurar Hora de Alarma")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Digital-7', 36))
        title_label.setStyleSheet("color: #00ff00; margin: 20px;")
        layout.addWidget(title_label)
        
        # Contenedor para hora
        hour_container = QVBoxLayout()
        hour_label = QLabel("HORA")
        hour_label.setAlignment(Qt.AlignCenter)
        hour_label.setStyleSheet("color: #00ff00;")
        
        # Botones de control para hora
        hour_up = QPushButton("▲")
        self.hour_display = QLabel("00")
        hour_down = QPushButton("▼")
        
        for widget in [hour_up, self.hour_display, hour_down]:
            widget.setFont(QFont('Digital-7', 48))
            widget.setStyleSheet("""
                QPushButton, QLabel { 
                    background-color: #003300; 
                    color: #00ff00; 
                    border: 2px solid #00ff00;
                    border-radius: 15px;
                    min-height: 80px;
                    min-width: 120px;
                }
                QPushButton:pressed {
                    background-color: #004400;
                }
            """)
        
        self.hour_display.setAlignment(Qt.AlignCenter)
        hour_up.clicked.connect(self.increment_hour)
        hour_down.clicked.connect(self.decrement_hour)
        
        # Contenedor para minutos
        minute_container = QVBoxLayout()
        minute_label = QLabel("MINUTOS")
        minute_label.setAlignment(Qt.AlignCenter)
        minute_label.setStyleSheet("color: #00ff00;")
        
        # Botones de control para minutos
        minute_up = QPushButton("▲")
        self.minute_display = QLabel("00")
        minute_down = QPushButton("▼")
        
        for widget in [minute_up, self.minute_display, minute_down]:
            widget.setFont(QFont('Digital-7', 48))
            widget.setStyleSheet("""
                QPushButton, QLabel { 
                    background-color: #003300; 
                    color: #00ff00; 
                    border: 2px solid #00ff00;
                    border-radius: 15px;
                    min-height: 80px;
                    min-width: 120px;
                }
                QPushButton:pressed {
                    background-color: #004400;
                }
            """)
        
        self.minute_display.setAlignment(Qt.AlignCenter)
        minute_up.clicked.connect(self.increment_minute)
        minute_down.clicked.connect(self.decrement_minute)
        
        # Organizar layouts
        time_layout = QHBoxLayout()
        for container, label, up, display, down in [
            (hour_container, hour_label, hour_up, self.hour_display, hour_down),
            (minute_container, minute_label, minute_up, self.minute_display, minute_down)
        ]:
            container.addWidget(label)
            container.addWidget(up)
            container.addWidget(display)
            container.addWidget(down)
            time_layout.addLayout(container)
        
        # Botones de control
        button_layout = QHBoxLayout()
        save_button = QPushButton("GUARDAR")
        cancel_button = QPushButton("CANCELAR")
        
        for button in [save_button, cancel_button]:
            button.setFont(QFont('Digital-7', 24))
            button.setStyleSheet("""
                QPushButton { 
                    background-color: #003300; 
                    color: #00ff00; 
                    border: 2px solid #00ff00;
                    border-radius: 15px;
                    min-height: 80px;
                    min-width: 200px;
                }
                QPushButton:pressed {
                    background-color: #004400;
                }
            """)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        # Agregar todo al layout principal
        layout.addLayout(time_layout)
        layout.addSpacing(40)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Valores iniciales
        self.current_hour = 7
        self.current_minute = 0
        self.update_displays()

    def increment_hour(self):
        self.current_hour = (self.current_hour + 1) % 24
        self.update_displays()

    def decrement_hour(self):
        self.current_hour = (self.current_hour - 1) % 24
        self.update_displays()

    def increment_minute(self):
        self.current_minute = (self.current_minute + 1) % 60
        self.update_displays()

    def decrement_minute(self):
        self.current_minute = (self.current_minute - 1) % 60
        self.update_displays()

    def update_displays(self):
        self.hour_display.setText(f"{self.current_hour:02d}")
        self.minute_display.setText(f"{self.current_minute:02d}")

    def get_alarm_time(self):
        return QTime(self.current_hour, self.current_minute)
