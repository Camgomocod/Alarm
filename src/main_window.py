from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QPoint
from PyQt5.QtGui import QFont, QFontDatabase
import datetime
from paths_config import FONT_PATH

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.setWindowTitle("Raspberry Pi Clock")
        self.setStyleSheet("background-color: #000000;")
        self.showFullScreen()
        
        # Cargar fuente retro
        font_id = QFontDatabase.addApplicationFont(FONT_PATH)
        if font_id == -1:
            print(f"Error: No se pudo cargar la fuente desde {FONT_PATH}")
        else:
            print(f"Fuente cargada exitosamente desde {FONT_PATH}")
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                self.font_family = font_families[0]
            else:
                self.font_family = 'Digital-7'
                print("Advertencia: No se encontraron familias de fuentes")
        
        # Crear layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Agregar espacio superior
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Crear un contenedor para el reloj
        clock_container = QWidget()
        clock_container.setStyleSheet("background-color: transparent;")
        clock_layout = QHBoxLayout(clock_container)
        clock_layout.setSpacing(10)
        
        # Crear los tres displays del reloj (horas, minutos, segundos)
        self.hours_label = QLabel()
        self.minutes_label = QLabel()
        self.seconds_label = QLabel()
        
        # Estilo común para todos los displays del reloj
        clock_style = """
            QLabel {
                color: #00ff00;
                background-color: #001100;
                border: 3px solid #003300;
                border-radius: 15px;
                padding: 10px;
                margin: 3px;
                min-width: 200px;
            }
        """
        
        # Aplicar estilo y configuración a cada display
        for label in [self.hours_label, self.minutes_label, self.seconds_label]:
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont(self.font_family, 140))
            label.setStyleSheet(clock_style)
        
        # Agregar los displays al layout
        clock_layout.addWidget(self.hours_label)
        clock_layout.addWidget(self.minutes_label)
        clock_layout.addWidget(self.seconds_label)
        
        # Agregar el contenedor del reloj al layout principal
        main_layout.addWidget(clock_container)
        
        # Fecha con estilo retro
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setFont(QFont(self.font_family, 36))
        self.date_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: #001100;
                border: 2px solid #003300;
                border-radius: 10px;
                padding: 15px;
                margin: 20px;
            }
        """)
        main_layout.addWidget(self.date_label)
        
        # Agregar espacio inferior
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Temporizador para actualizar la hora
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        self.update_time()

    def update_time(self):
        current_time = datetime.datetime.now()
        
        # Actualizar la hora
        self.hours_label.setText(current_time.strftime("%H"))
        self.minutes_label.setText(current_time.strftime("%M"))
        self.seconds_label.setText(current_time.strftime("%S"))
        
        # Actualizar la fecha
        self.date_label.setText(current_time.strftime("%A, %d de %B de %Y").upper())
        
        # Añadir animación suave al cambiar números
        for label in [self.hours_label, self.minutes_label, self.seconds_label]:
            anim = QPropertyAnimation(label, b"pos")
            anim.setDuration(200)
            anim.setStartValue(label.pos() + QPoint(0, 5))
            anim.setEndValue(label.pos())
            anim.start()