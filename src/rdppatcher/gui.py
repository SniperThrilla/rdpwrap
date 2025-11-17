# gui.py

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QTextEdit
from rdppatcher.logic import Worker
import sys

class PatcherUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RDP Patcher")
        self.resize(600, 400)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(8)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setLineWrapMode(QTextEdit.NoWrap)
        self.console.setMinimumHeight(300)

        self.btn = QPushButton("Run Patcher")
        self.btn.clicked.connect(self.run_patch)
        self.set_disabled_readable(self.btn)

        self.main_layout.addWidget(self.console)
        self.main_layout.addWidget(self.btn)

        self.setLayout(self.main_layout)
        
        self.worker = None

    def set_disabled_readable(self, button: QPushButton):
        button.setStyleSheet("QPushButton:disabled { color: #cccccc; }")

    def log(self, text):
        self.console.append(text)
        self.console.ensureCursorVisible()

    def finish_patch(self, success):
        if success:
            self.btn.setText("Finish")
        else:
            self.btn.setText("Quit")
        self.btn.clicked.connect(self.close)
        self.btn.setEnabled(True)

    def run_patch(self):
        self.btn.setEnabled(False)
        self.btn.clicked.disconnect()
        self.btn.setText("Running...")
        self.worker = Worker()
        self.worker.log.connect(self.log)
        self.worker.done.connect(self.finish_patch)
        self.worker.start()

def main():
    app = QApplication(sys.argv)
    window = PatcherUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

