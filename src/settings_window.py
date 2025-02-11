from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtGui import QFont

class AlarmSettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Alarma")
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        # Establecer un tamaño fijo más pequeño
        self.setFixedSize(280, 400)
        
        self.setStyleSheet("""
            QDialog { 
                background-color: #000000;
            }
            QLabel { 
                color: #00ff00; 
                font-size: 20px;
                font-family: 'Digital-7';
            }
            QPushButton { 
                background-color: #003300; 
                color: #00ff00; 
                border: 2px solid #00ff00;
                border-radius: 8px;
                min-height: 35px;
                min-width: 80px;
                font-size: 18px;
                font-family: 'Digital-7';
            }
            QPushButton:hover {
                background-color: #004400;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Reducir el espaciado entre elementos
        
        # Título más pequeño
        title_label = QLabel("Configurar Alarma")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Digital-7', 24))
        title_label.setStyleSheet("color: #00ff00; margin: 10px;")
        layout.addWidget(title_label)
        
        # Contenedor tiempo
        time_layout = QHBoxLayout()
        time_layout.setSpacing(15)  # Espacio entre hora y minutos
        
        # Función helper para crear controles de tiempo
        def create_time_control(label_text):
            container = QVBoxLayout()
            container.setSpacing(5)  # Reducir espacio entre elementos
            
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignCenter)
            
            up = QPushButton("▲")
            display = QLabel("00")
            down = QPushButton("▼")
            
            for widget in [up, display, down]:
                widget.setFixedSize(80, 50)  # Tamaño fijo para todos los elementos
                widget.setFont(QFont('Digital-7', 28))
                widget.setStyleSheet("""
                    QLabel, QPushButton { 
                        background-color: #003300; 
                        color: #00ff00; 
                        border: 2px solid #00ff00;
                        border-radius: 8px;
                    }
                    QPushButton:pressed {
                        background-color: #004400;
                    }
                """)
            
            display.setAlignment(Qt.AlignCenter)
            
            container.addWidget(label)
            container.addWidget(up)
            container.addWidget(display)
            container.addWidget(down)
            
            return container, display, up, down
        
        # Crear controles de hora y minutos
        hour_container, self.hour_display, hour_up, hour_down = create_time_control("HORA")
        minute_container, self.minute_display, minute_up, minute_down = create_time_control("MIN")
        
        hour_up.clicked.connect(self.increment_hour)
        hour_down.clicked.connect(self.decrement_hour)
        minute_up.clicked.connect(self.increment_minute)
        minute_down.clicked.connect(self.decrement_minute)
        
        time_layout.addLayout(hour_container)
        time_layout.addLayout(minute_container)
        
        # Botones de control más pequeños
        button_layout = QHBoxLayout()
        save_button = QPushButton("GUARDAR")
        cancel_button = QPushButton("CANCELAR")
        
        for button in [save_button, cancel_button]:
            button.setFixedSize(120, 40)
            button.setFont(QFont('Digital-7', 18))
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        # Organizar layout
        layout.addLayout(time_layout)
        layout.addSpacing(20)
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
        # Forzar actualización inmediata
        self.hour_display.setText(f"{self.current_hour:02d}")
        self.minute_display.setText(f"{self.current_minute:02d}")
        self.hour_display.repaint()
        self.minute_display.repaint()

    def get_alarm_time(self):
        return QTime(self.current_hour, self.current_minute)
