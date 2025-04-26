import sys
import os
import subprocess
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QProgressBar
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PIL import Image
import base64

class SolverThread(QThread):
    update_status = pyqtSignal(str)
    update_image = pyqtSignal(str)
    update_progress = pyqtSignal(int)

    def run(self):
        self.update_status.emit("Iniciando navegador...")
        self.update_progress.emit(20)
        result = subprocess.run(['node', 'browser.js'], capture_output=True, text=True)
        try:
            data = json.loads(result.stdout)
            if data['image']:
                with open("captcha.png", "wb") as f:
                    f.write(base64.b64decode(data['image']))
                self.update_image.emit("captcha.png")
                self.update_progress.emit(50)
                lua_result = subprocess.run(['lua', 'solver.lua', 'captcha.png'], capture_output=True, text=True)
                solved_text = lua_result.stdout.strip()
                self.update_status.emit(f"CAPTCHA resuelto: {solved_text}")
                self.update_progress.emit(100)
            else:
                self.update_status.emit(f"Error: {data['result']}")
                self.update_progress.emit(0)
        except Exception as e:
            self.update_status.emit(f"Error: {str(e)}")
            self.update_progress.emit(0)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solucionador de CAPTCHA")
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(400, 300)
        self.layout.addWidget(self.image_label)
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.layout.addWidget(self.status_text)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.progress_bar)
        self.button_layout = QHBoxLayout()
        self.start_button = QPushButton("Iniciar Solución")
        self.clear_button = QPushButton("Limpiar")
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.clear_button)
        self.layout.addLayout(self.button_layout)
        self.start_button.clicked.connect(self.start_solving)
        self.clear_button.clicked.connect(self.clear_output)
        self.thread = None

    def start_solving(self):
        if self.thread is None or not self.thread.isRunning():
            self.thread = SolverThread()
            self.thread.update_status.connect(self.update_status)
            self.thread.update_image.connect(self.update_image)
            self.thread.update_progress.connect(self.progress_bar.setValue)
            self.thread.start()

    def update_status(self, text):
        self.status_text.append(text)

    def update_image(self, image_path):
        image = QImage(image_path)
        if not image.isNull():
            pixmap = QPixmap.fromImage(image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def clear_output(self):
        self.status_text.clear()
        self.image_label.clear()
        self.progress_bar.setValue(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())