from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QPushButton, QMessageBox, QHBoxLayout, QDialog
from PyQt5.QtCore import QTimer, Qt, QTime
from PyQt5.QtGui import QFont, QFontDatabase
import pygame
from settings_window import AlarmSettingsWindow
import datetime
import requests
import json
import logging

class MainWindow(QMainWindow):
    # Configuraciones del clima
    WEATHER_APP_ID = "e2c5c5e4"
    WEATHER_APP_KEY = "519d24835c42f18e42f8bfc8f64c3e6a"
    LATITUDE = "2.4448"
    LONGITUDE = "-76.6147"

    def __init__(self):
        super().__init__()
        
        # Inicializar pygame antes de cualquier otra cosa
        pygame.init()
        pygame.mixer.init(44100, -16, 2, 2048)
        
        # Configuración de la ventana
        self.setWindowTitle("Raspberry Pi Alarm")
        self.setStyleSheet("background-color: #000000;")
        self.showFullScreen()  # Asegurar pantalla completa
        
        # Cargar fuente retro
        QFontDatabase.addApplicationFont("/mnt/c/Users/Usuario/Projects/Alarm/fonts/digital-7.ttf")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Agregar espacio superior
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Reloj digital con nueva fuente y color (más grande)
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont('Digital-7', 180))  # Aumentado a 180
        self.time_label.setStyleSheet("color: #00ff00;")
        
        # Fecha con estilo retro
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setFont(QFont('Digital-7', 36))
        self.date_label.setStyleSheet("color: #00ff00;")
        
        # Widget del clima con estilo retro
        self.weather_label = QLabel()
        self.weather_label.setAlignment(Qt.AlignCenter)
        self.weather_label.setFont(QFont('Digital-7', 24))
        self.weather_label.setStyleSheet("color: #00ff00;")
        
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)
        
        # Agregar espacio entre fecha y clima
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        layout.addWidget(self.weather_label)
        
        # Contenedor para botón y etiqueta de alarma (sin borde)
        alarm_container = QWidget()
        alarm_container.setStyleSheet("background-color: transparent;")
        alarm_layout = QHBoxLayout(alarm_container)
        alarm_layout.setContentsMargins(10, 10, 10, 10)  # Reducir márgenes
        
        # Botón de alarma con estilo retro (reducido)
        self.alarm_button = QPushButton("|| ALARMA")
        self.alarm_button.setFont(QFont('Digital-7', 20))  # Reducido a 20
        self.alarm_button.setStyleSheet("""
            QPushButton { 
                background-color: #003300; 
                color: #00ff00; 
                border: 2px solid #00ff00;
                border-radius: 10px;
                min-height: 50px;
                min-width: 120px;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #004400;
            }
            QPushButton:hover {
                border: 3px solid #00ff00;
            }
        """)
        self.alarm_button.setCursor(Qt.PointingHandCursor)
        # Asegurar que la conexión sea correcta
        self.alarm_button.clicked.connect(lambda: self.show_alarm_settings())
        
        # Etiqueta para mostrar la alarma configurada (reducida)
        self.alarm_label = QLabel("No hay alarma configurada")
        self.alarm_label.setAlignment(Qt.AlignCenter)
        self.alarm_label.setFont(QFont('Digital-7', 20))  # Reducido a 20
        self.alarm_label.setStyleSheet("color: #00ff00;")
        
        # Organizar botón y etiqueta horizontalmente
        alarm_layout.addWidget(self.alarm_button)
        alarm_layout.addWidget(self.alarm_label)
        
        # Agregar el contenedor de alarma al layout principal
        layout.addItem(QSpacerItem(20, 20))
        layout.addWidget(alarm_container)
        
        # Configuración de la alarma y sonido
        self.alarm_time = None
        
        # Configuración del sonido
        try:
            pygame.mixer.init()
            self.alarm_sound = pygame.mixer.Sound("/mnt/c/Users/Usuario/Projects/Alarm/sounds/alarm.wav")
            self.alarm_sound.set_volume(1.0)  # Volumen al máximo
        except Exception as e:
            print(f"Error inicializando sonido: {e}")
            logging.error(f"Error inicializando sonido: {e}")
            self.alarm_sound = None
        
        # Temporizadores
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(10000)  # Primer update en 10 segundos
        
        # Configurar logging
        logging.basicConfig(
            filename='weather_debug.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.update_time()
        self.update_weather()

    def show_alarm_settings(self):
        try:
            dialog = AlarmSettingsWindow(self)
            dialog.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)  # Hacer la ventana más apropiada para táctil
            dialog.move(self.rect().center() - dialog.rect().center())  # Centrar el diálogo
            
            if dialog.exec_() == QDialog.Accepted:
                self.alarm_time = dialog.get_alarm_time()
                self.alarm_label.setText(f"|| {self.alarm_time.toString('HH:mm')}")
                # Agregar feedback visual
                self.alarm_button.setStyleSheet(self.alarm_button.styleSheet() + "background-color: #004400;")
                QTimer.singleShot(200, lambda: self.alarm_button.setStyleSheet(self.alarm_button.styleSheet()))
        except Exception as e:
            print(f"Error mostrando configuración de alarma: {e}")
    
    def update_time(self):
        current_time = datetime.datetime.now()
        self.time_label.setText(current_time.strftime("%H:%M:%S"))
        self.date_label.setText(current_time.strftime("%A, %d %B %Y"))
        
        # Verificar alarma
        if self.alarm_time:
            current_qtime = QTime.currentTime()
            if current_qtime.hour() == self.alarm_time.hour() and \
               current_qtime.minute() == self.alarm_time.minute() and \
               current_qtime.second() == 0:
                try:
                    self.alarm_sound.play()
                except:
                    print("Error reproduciendo sonido de alarma")
                self.show_alarm_dialog()

    def show_alarm_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #000000;
                border: 2px solid #00ff00;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Mensaje de alarma
        message = QLabel("¡DESPERTAR!")
        message.setAlignment(Qt.AlignCenter)
        message.setFont(QFont('Digital-7', 72))
        message.setStyleSheet("color: #00ff00; margin: 20px;")
        
        # Botón de apagar alarma
        stop_button = QPushButton("DETENER ALARMA")
        stop_button.setFont(QFont('Digital-7', 36))
        stop_button.setStyleSheet("""
            QPushButton {
                background-color: #003300;
                color: #00ff00;
                border: 2px solid #00ff00;
                border-radius: 15px;
                min-width: 300px;
                min-height: 80px;
                margin: 20px;
            }
            QPushButton:pressed {
                background-color: #004400;
            }
            QPushButton:hover {
                border: 3px solid #00ff00;
            }
        """)
        
        layout.addWidget(message)
        layout.addWidget(stop_button)
        
        # Centrar el diálogo en la pantalla
        dialog.setFixedSize(400, 300)
        dialog.move(
            self.frameGeometry().center() - dialog.frameGeometry().center()
        )
        
        # Conectar el botón para detener la alarma
        stop_button.clicked.connect(lambda: self.stop_alarm_and_close(dialog))
        
        if self.alarm_sound:
            try:
                pygame.mixer.stop()  # Detener cualquier sonido previo
                self.alarm_sound.play(loops=-1)  # Reproducir en loop
            except Exception as e:
                print(f"Error reproduciendo sonido: {e}")
                logging.error(f"Error reproduciendo sonido: {e}")
        
        dialog.show()

    def stop_alarm_and_close(self, dialog):
        if self.alarm_sound:
            try:
                pygame.mixer.stop()
            except Exception as e:
                print(f"Error deteniendo sonido: {e}")
        dialog.close()
        
        # Mantener la alarma configurada para el día siguiente
        if self.alarm_time:
            self.alarm_label.setText(f"|| Próxima alarma: {self.alarm_time.toString('HH:mm')}")

    def update_weather(self):
        try:
            # Construir URL con los parámetros de autenticación en la query
            base_url = f"http://api.weatherunlocked.com/api/current/{self.LATITUDE},{self.LONGITUDE}"
            url = f"{base_url}?app_id={self.WEATHER_APP_ID}&app_key={self.WEATHER_APP_KEY}"
            
            logging.debug("Intentando conectar a WeatherUnlocked...")
            
            # Hacer la petición sin headers de autenticación
            response = requests.get(url, timeout=10)
            logging.debug(f"Código de estado HTTP: {response.status_code}")
            logging.debug(f"URL completa: {url}")  # Para debug
            
            if response.status_code != 200:
                self.weather_label.setText(f"Error API: {response.status_code}")
                logging.error(f"Error API: {response.status_code} - {response.text}")
                return
            
            data = response.json()
            logging.debug(f"Respuesta: {data}")
            
            if 'temp_c' in data and 'humid_pct' in data:
                temp = data['temp_c']
                humidity = data['humid_pct']
                description = data.get('wx_desc', '')
                
                # Mostrar información del clima
                weather_text = (f"> {temp:.1f}°C | {description}\n"
                              f"> Humedad: {humidity}%")
                
                self.weather_label.setText(weather_text)
                logging.info(f"Clima actualizado exitosamente: {weather_text}")
                
                # Cambiar intervalo a 30 minutos si fue exitoso
                self.weather_timer.setInterval(1800000)
            else:
                raise KeyError("Datos del clima incompletos")
                
        except requests.ConnectionError as e:
            error_msg = "Error de conexión. Verificando internet..."
            self.weather_label.setText(error_msg)
            logging.error(f"{error_msg}\n{str(e)}")
            
        except requests.Timeout:
            error_msg = "Tiempo de espera agotado"
            self.weather_label.setText(error_msg)
            logging.error(error_msg)
            
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            self.weather_label.setText(error_msg)
            logging.error(error_msg)
