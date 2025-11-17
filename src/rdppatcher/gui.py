# gui.py

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QTextEdit
from rdppatcher.logic import Worker
import sys

class PatcherUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RDP Patcher")

        self.main_layout = QVBoxLayout()

        self.console = QTextEdit()
        self.console.setReadOnly(True)

        self.btn = QPushButton("Run Patcher")
        self.btn.clicked.connect(self.run_patch)

        self.ok_btn = QPushButton("Finish")
        self.ok_btn.setVisible(False)
        self.ok_btn.clicked.connect(self.close)

        self.main_layout.addWidget(self.console)
        self.main_layout.addWidget(self.btn)
        self.main_layout.addWidget(self.ok_btn)

        self.setLayout(self.main_layout)

        self.proc = None

    def log(self, text):
        self.console.append(text)
        self.console.ensureCursorVisible()

    def finish_patch(self):
        self.ok_btn.setVisible(True)

    def run_patch(self):
        self.btn.setVisible(False)
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

