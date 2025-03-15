from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QPushButton, QMessageBox, QHBoxLayout, QDialog
from PyQt5.QtCore import QTimer, Qt, QTime
from PyQt5.QtGui import QFont, QFontDatabase
import pygame
import threading
import os
import logging
from settings_window import AlarmSettingsWindow
import datetime
import requests
import json
from playsound import playsound
from paths_config import FONT_PATH, ALARM_SOUND_PATH, LOG_FILE_PATH
from emoji_animation import EmojiWidget
import vlc

class MainWindow(QMainWindow):
    # Configuraciones del clima
    WEATHER_APP_ID = "e2c5c5e4"
    WEATHER_APP_KEY = "519d24835c42f18e42f8bfc8f64c3e6a"
    LATITUDE = "2.4448"
    LONGITUDE = "-76.6147"

    def __init__(self):
        super().__init__()
        
        # Inicializar pygame para audio
        pygame.mixer.init()
        self.alarm_sound_file = ALARM_SOUND_PATH
        self.is_alarm_playing = False
        
        try:
            pygame.mixer.music.load(self.alarm_sound_file)
            print("Sonido cargado correctamente")
        except Exception as e:
            print(f"Error cargando sonido: {e}")
            logging.error(f"Error cargando sonido: {e}")
        
        # Configuración de la ventana
        self.setWindowTitle("Raspberry Pi Alarm")
        self.setStyleSheet("background-color: #000000;")
        self.showFullScreen()  # Asegurar pantalla completa
        
        # Cargar fuente retro
        QFontDatabase.addApplicationFont(FONT_PATH)
        
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
                min-width: 150px;
            }
        """
        
        # Aplicar estilo y configuración a cada display
        for label in [self.hours_label, self.minutes_label, self.seconds_label]:
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont('Digital-7', 120))
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
        self.date_label.setFont(QFont('Digital-7', 24))
        self.date_label.setStyleSheet("color: #00ff00;")
        main_layout.addWidget(self.date_label)
        
        # Widget del clima con estilo retro
        self.weather_label = QLabel()
        self.weather_label.setAlignment(Qt.AlignCenter)
        self.weather_label.setFont(QFont('Digital-7', 20))
        self.weather_label.setStyleSheet("color: #00ff00;")
        main_layout.addWidget(self.weather_label)
        
        # Añadir emoji animation
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.emoji = EmojiWidget()
        self.emoji.setFixedHeight(80)
        main_layout.addWidget(self.emoji, alignment=Qt.AlignCenter)
        
        # Contenedor para botón y etiqueta de alarma
        alarm_container = QWidget()
        alarm_container.setStyleSheet("""
            QWidget {
                background-color: #001100;
                border: 2px solid #003300;
                border-radius: 15px;
                padding: 5px;
            }
        """)
        alarm_layout = QHBoxLayout(alarm_container)
        alarm_layout.setContentsMargins(20, 15, 20, 15)
        
        # Botón de alarma con estilo retro actualizado
        self.alarm_button = QPushButton("|| ALARMA")
        self.alarm_button.setFont(QFont('Digital-7', 24))
        self.alarm_button.setStyleSheet("""
            QPushButton { 
                background-color: #003300; 
                color: #00ff00; 
                border: 2px solid #00ff00;
                border-radius: 10px;
                min-height: 50px;
                min-width: 130px;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #004400;
            }
            QPushButton:hover {
                border: 3px solid #00ff00;
                background-color: #003300;
            }
        """)
        self.alarm_button.setCursor(Qt.PointingHandCursor)
        # Asegurar que la conexión sea correcta
        self.alarm_button.clicked.connect(lambda: self.show_alarm_settings())
        
        # Etiqueta para mostrar la alarma configurada
        self.alarm_label = QLabel("No hay alarma configurada")
        self.alarm_label.setAlignment(Qt.AlignCenter)
        self.alarm_label.setFont(QFont('Digital-7', 24))
        self.alarm_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: #001100;
                border: 2px solid #003300;
                border-radius: 10px;
                padding: 10px 20px;
                min-width: 300px;
            }
        """)
        
        # Organizar botón y etiqueta horizontalmente
        alarm_layout.addWidget(self.alarm_button)
        alarm_layout.addWidget(self.alarm_label)
        
        # Agregar el contenedor de alarma al layout principal
        main_layout.addItem(QSpacerItem(20, 20))
        main_layout.addWidget(alarm_container)
        main_layout.addStretch()
        
        # Configuración de la alarma y sonido
        self.alarm_time = None
        
        # Temporizadores
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(900000)  # 15 minutos = 900000 milisegundos
        
        # Configurar logging
        logging.basicConfig(
            filename=LOG_FILE_PATH,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.update_time()
        self.update_weather()

        # Inicializar python-vlc media player para reproducir el sonido de alarma
        self.alarm_sound_file = ALARM_SOUND_PATH
        self.vlc_instance = vlc.Instance()
        media_list = self.vlc_instance.media_list_new([self.alarm_sound_file])
        self.alarmPlayer = self.vlc_instance.media_list_player_new()
        self.alarmPlayer.set_media_list(media_list)
        self.alarmPlayer.set_playback_mode(vlc.PlaybackMode.loop)
        self.is_alarm_playing = False

    def play_alarm_sound(self):
        """Reproduce el sonido de la alarma en loop usando MediaListPlayer"""
        try:
            if not self.is_alarm_playing:
                self.is_alarm_playing = True
                self.alarmPlayer.play()                
                print("Reproduciendo alarma en loop con MediaListPlayer...")
        except Exception as e:
            print(f"Error reproduciendo sonido: {e}")
            logging.error(f"Error reproduciendo sonido: {e}")

    def stop_alarm_sound(self):
        """Detiene el sonido de la alarma y desactiva el loop"""
        try:
            self.is_alarm_playing = False
            self.alarmPlayer.stop()
            print("Alarma detenida")
        except Exception as e:
            print(f"Error deteniendo sonido: {e}")
            logging.error(f"Error deteniendo sonido: {e}")

    def show_alarm_settings(self):
        try:
            dialog = AlarmSettingsWindow(self)
            dialog.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)  # Hacer la ventana más apropiada para táctil
            dialog.move(self.rect().center() - dialog.rect().center())  # Centrar el diálogo
            
            if dialog.exec_() == QDialog.Accepted:
                self.alarm_time = dialog.get_alarm_time()
                self.alarm_label.setText(f"▶ {self.alarm_time.toString('HH:mm')} ◀")
                # Agregar feedback visual
                self.alarm_button.setStyleSheet(self.alarm_button.styleSheet() + "background-color: #004400;")
                QTimer.singleShot(200, lambda: self.alarm_button.setStyleSheet(self.alarm_button.styleSheet()))
        except Exception as e:
            print(f"Error mostrando configuración de alarma: {e}")
    
    def update_time(self):
        current_time = datetime.datetime.now()
        self.hours_label.setText(current_time.strftime("%H"))
        self.minutes_label.setText(current_time.strftime("%M"))
        self.seconds_label.setText(current_time.strftime("%S"))
        self.date_label.setText(current_time.strftime("%A, %d %B %Y").upper())  # Mayúsculas para estilo retro
        
        # Verificar alarma
        if self.alarm_time:
            current_qtime = QTime.currentTime()
            if current_qtime.hour() == self.alarm_time.hour() and \
               current_qtime.minute() == self.alarm_time.minute() and \
               current_qtime.second() == 0:
                try:
                    self.play_alarm_sound()
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
        
        self.play_alarm_sound()  # Reproducir sonido cuando se muestra el diálogo
        
        dialog.show()

    def stop_alarm_and_close(self, dialog):
        self.stop_alarm_sound()  # Detener sonido cuando se cierra el diálogo
        dialog.close()
        
        # Mantener la alarma configurada para el día siguiente
        if self.alarm_time:
            self.alarm_label.setText(f"▶ Próxima alarma: {self.alarm_time.toString('HH:mm')} ◀")

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
                temp = data['temp_c'] - 6  # Restar 6 grados a la temperatura
                humidity = data['humid_pct']
                description = data.get('wx_desc', '')
                
                # Mostrar información del clima con la temperatura ajustada
                weather_text = (f"> {temp:.1f}°C | {description}\n"
                              f"> Humedad: {humidity}%")
                
                self.weather_label.setText(weather_text)
                logging.info(f"Clima actualizado exitosamente: {weather_text}")
                
                # Cambiar intervalo a 15 minutos después de una actualización exitosa
                self.weather_timer.setInterval(900000)
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