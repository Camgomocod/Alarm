from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QPushButton, QMessageBox, QHBoxLayout, QDialog, QScrollArea
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
from calendar_handler import CalendarHandler
from emoji_animation import EmojiWidget

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
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Crear layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        
        # Contenedor izquierdo (60%)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        # Contenedor derecho (35%)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        
        # Configurar proporciones
        main_layout.addWidget(left_container, 65)  # Aumentar proporción izquierda
        main_layout.addWidget(right_container, 32)  # Reducir proporción derecha
        main_layout.setSpacing(5)  # Reducir espacio entre contenedores
        
        # Mover el código existente del reloj, fecha y clima al contenedor izquierdo
        # Agregar espacio superior
        left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Crear un contenedor para el reloj
        clock_container = QWidget()
        clock_container.setStyleSheet("background-color: transparent;")
        clock_layout = QHBoxLayout(clock_container)
        clock_layout.setSpacing(10)  # Reducido de 20 a 10
        
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
            label.setFont(QFont('Digital-7', 120))  # Reducido de 180 a 120
            label.setStyleSheet(clock_style)
        
        # Agregar los displays al layout
        clock_layout.addWidget(self.hours_label)
        clock_layout.addWidget(self.minutes_label)
        clock_layout.addWidget(self.seconds_label)
        
        # Agregar el contenedor del reloj al layout principal
        left_layout.addWidget(clock_container)
        
        # Fecha con estilo retro (ligeramente más pequeña)
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setFont(QFont('Digital-7', 24))  # Reducido de 30 a 24
        self.date_label.setStyleSheet("color: #00ff00;")
        
        # Widget del clima con estilo retro
        self.weather_label = QLabel()
        self.weather_label.setAlignment(Qt.AlignCenter)
        self.weather_label.setFont(QFont('Digital-7', 20))  # Reducido de 24 a 20
        self.weather_label.setStyleSheet("color: #00ff00;")
        
        left_layout.addWidget(self.date_label)
        
        # Agregar espacio entre fecha y clima
        left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        left_layout.addWidget(self.weather_label)
        
        # Añadir espacio antes del emoji (reducido)
        left_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Añadir emoji animation con tamaño fijo
        self.emoji = EmojiWidget()
        self.emoji.setFixedHeight(80)  # Reducido de 100 a 80
        left_layout.addWidget(self.emoji, alignment=Qt.AlignCenter)
        
        # Reducir el espacio entre el emoji y el contenedor de alarma
        left_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
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
        left_layout.addItem(QSpacerItem(20, 20))
        left_layout.addWidget(alarm_container)
        left_layout.addStretch()
        
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

        # Después del contenedor de alarma, agregar el widget de agenda
        # Crear widget de agenda
        agenda_container = QWidget()
        agenda_container.setStyleSheet("""
            QWidget {
                background-color: #001100;
                border: 2px solid #003300;
                border-radius: 15px;
                padding: 5px;
                margin: 5px;
            }
        """)
        
        # Título de la agenda
        agenda_title = QLabel("AGENDA")
        agenda_title.setFont(QFont('Digital-7', 20))  # Reducido de 24 a 20
        agenda_title.setStyleSheet("""
            color: #00ff00;
            padding: 5px;
            margin-bottom: 5px;
        """)
        agenda_title.setAlignment(Qt.AlignCenter)
        
        # Lista de eventos
        self.events_widget = QWidget()
        self.events_layout = QVBoxLayout(self.events_widget)
        self.events_layout.setSpacing(5)
        
        # Lista de eventos con scroll
        events_scroll = QScrollArea()
        events_scroll.setWidget(self.events_widget)
        events_scroll.setWidgetResizable(True)
        events_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
                margin: 0px;
                padding: 0px;
            }
            QScrollBar:vertical {
                background: #001100;
                width: 6px;
                border-radius: 3px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #003300;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        agenda_layout = QVBoxLayout(agenda_container)
        agenda_layout.setContentsMargins(5, 5, 5, 5)
        agenda_layout.setSpacing(5)
        agenda_layout.addWidget(agenda_title)
        agenda_layout.addWidget(events_scroll)
        
        right_layout.addWidget(agenda_container)
        
        # Inicializar el manejador de calendario
        try:
            self.calendar_handler = CalendarHandler()
            # Timer para actualizar eventos cada 5 minutos
            self.calendar_timer = QTimer()
            self.calendar_timer.timeout.connect(self.update_events)
            self.calendar_timer.start(300000)  # 5 minutos = 300000 milisegundos
            # Primera actualización inmediata
            self.update_events()
        except Exception as e:
            logging.error(f"Error inicializando Calendar Handler: {e}")

    def play_alarm_sound(self):
        """Reproduce el sonido de la alarma en loop"""
        try:
            if not self.is_alarm_playing:
                self.is_alarm_playing = True
                pygame.mixer.music.play(-1)  # -1 significa loop infinito
                print("Reproduciendo alarma...")
        except Exception as e:
            print(f"Error reproduciendo sonido: {e}")
            logging.error(f"Error reproduciendo sonido: {e}")

    def stop_alarm_sound(self):
        """Detiene el sonido de la alarma"""
        try:
            pygame.mixer.music.stop()
            self.is_alarm_playing = False
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

    def update_events(self):
        try:
            # Limpiar eventos anteriores
            for i in reversed(range(self.events_layout.count())): 
                self.events_layout.itemAt(i).widget().setParent(None)
            
            events = self.calendar_handler.get_todays_events()
            
            if not events:
                no_events = QLabel("No hay eventos programados")
                no_events.setFont(QFont('Digital-7', 18))  # Reducido de 20 a 18
                no_events.setStyleSheet("color: #00ff00;")
                no_events.setAlignment(Qt.AlignCenter)
                self.events_layout.addWidget(no_events)
            else:
                for event in events:
                    # Crear contenedor para cada evento
                    event_widget = QWidget()
                    event_layout = QVBoxLayout(event_widget)
                    event_layout.setContentsMargins(10, 12, 10, 12)  # Aumentar márgenes internos
                    event_layout.setSpacing(4)  # Más espacio entre hora y título
                    
                    # Hora del evento
                    time_label = QLabel(event['time'])
                    time_label.setFont(QFont('Digital-7', 18))  # Reducido de 22 a 18
                    time_label.setStyleSheet("""
                        color: #00ff00;
                        padding: 2px;
                    """)
                    
                    # Título del evento
                    title_label = QLabel(event['summary'])
                    title_label.setFont(QFont('Digital-7', 20))  # Reducido de 24 a 20
                    title_label.setStyleSheet("""
                        color: #00ff00;
                        padding: 2px;
                    """)
                    title_label.setWordWrap(True)
                    
                    event_layout.addWidget(time_label)
                    event_layout.addWidget(title_label)
                    
                    event_widget.setStyleSheet("""
                        QWidget {
                            background-color: #002200;
                            border-radius: 6px;
                            padding: 5px;
                            margin: 2px;
                        }
                    """)
                    
                    self.events_layout.addWidget(event_widget)
                
                # Ajustar el espaciado entre eventos
                self.events_layout.setSpacing(8)  # Aumentado de 4 a 8
            
            # Ajustar el espaciado del layout de eventos
            self.events_layout.setContentsMargins(4, 4, 4, 4)
            
        except Exception as e:
            logging.error(f"Error actualizando eventos: {e}")
            error_widget = QLabel("Error cargando eventos")
            error_widget.setFont(QFont('Digital-7', 20))
            error_widget.setStyleSheet("color: #ff0000;")
            self.events_layout.addWidget(error_widget)
