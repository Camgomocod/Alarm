import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()  # Cambiado de showFullScreen() a show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error iniciando la aplicación: {e}")
