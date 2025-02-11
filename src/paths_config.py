import os

# Obtener el directorio base del proyecto
if os.path.exists('/home/baysi/Projects/Alarm'):
    # Estamos en Raspberry Pi
    BASE_DIR = '/home/baysi/Projects/Alarm'
else:
    # Estamos en Windows/WSL
    BASE_DIR = '/mnt/c/Users/Usuario/Projects/Alarm'

# Definir las rutas relativas al directorio base
FONTS_DIR = os.path.join(BASE_DIR, 'fonts')
SOUNDS_DIR = os.path.join(BASE_DIR, 'sounds')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Asegurar que los directorios existan
for directory in [FONTS_DIR, SOUNDS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Rutas específicas de archivos
FONT_PATH = os.path.join(FONTS_DIR, 'digital-7.ttf')
ALARM_SOUND_PATH = os.path.join(SOUNDS_DIR, 'alarm.wav')
LOG_FILE_PATH = os.path.join(LOGS_DIR, 'weather_debug.log')
