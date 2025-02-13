from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

class EmojiWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame = 0
        self.initUI()

    def initUI(self):
        # Crear layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.display = QLabel()
        self.display.setFont(QFont('Digital-7', 36))  # Aumentar tamaño de fuente
        self.display.setAlignment(Qt.AlignCenter)
        self.display.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: #001100;
                border: 2px solid #003300;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
                min-height: 60px;
            }
        """)
        
        layout.addWidget(self.display)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_emoji)
        self.timer.start(10000)
        
        self.update_emoji()

    def update_emoji(self):
        emojis = [
            "(｡◕‿◕｡)",
            "( ╥﹏╥)ノシ",
            "(✿◠‿◠)",
            "≽^•⩊•^≼",
            "(◕‿◕✿)",
            "ヽ(^o^)ノ",
            "   :P   "
        ]
        
        self.display.setText(emojis[self.frame])
        self.frame = (self.frame + 1) % len(emojis)
