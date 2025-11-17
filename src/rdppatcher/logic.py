# logic.py

import subprocess
from PySide6.QtCore import QThread, Signal
import os, sys
from datetime import datetime
from pathlib import Path

RDP_FOLDER = "C:\\Program Files\\RDP Patcher"
INI_PATH = os.path.join(RDP_FOLDER, "rdpwrap.ini")

class Worker(QThread):
    log = Signal(str)
    done = Signal()

    def run(self):
        self.log.emit("Disabling active RDP services...")
        if not self.run_program(["net", "stop", "TermService", "/y"]):
            return self.fail()

        self.log.emit("Running Offset Finder...")
        offset_finder = self.bundled("OffsetFinder.exe")
        if (offsets := self.run_program([offset_finder])) is None:
            return self.fail()

        self.log.emit("Creating rdpwrap.ini...")
        if not self.create_ini(offsets):
            return self.fail()

        self.log.emit("Re-enabling RDP services...")
        if not self.run_program(["net", "start", "TermService", "/y"]):
            return self.fail()

        self.log.emit("Finished!")
        self.done.emit()

    def fail(self):
        self.log.emit("An error has occurred...")
        self.done.emit()

    def bundled(self, path):
        base = getattr(sys, "_MEIPASS", os.path.abspath("."))
        return os.path.join(base, path)

    def run_program(self, args):
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode:
            # Process failed to run.
            self.log.emit(f"**FAILED** - {' '.join(args)}")
            self.log.emit("STDOUT:")
            self.log.emit(result.stdout)
            self.log.emit("STDERR:")
            self.log.emit(result.stderr)
            return None
        return result.stdout

    def move_ini(self):
        if os.path.exists(INI_PATH):
            os.rename(INI_PATH, RDP_FOLDER + f"rdpwrap.ini.{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")

    def create_ini(self, text: str):
        try:
            self.move_ini()
            template_path = self.bundled("resources/template.ini")
            template = Path(template_path).read_text()

            regular_values, slinit_values = self.process_output(text)
            template = template.format(regular_values=regular_values, slinit_values=slinit_values)

            Path(INI_PATH).write_text(template)

            self.log.emit(f"New rdpwrap.ini written to {INI_PATH}")
            return True

        except Exception as e:
            self.log.emit(f"Unable to create new rdpwrap.ini: {e}")
            return False

    def process_output(self, main_values):
        main_values = main_values.replace("\r\n", "\n")
        slinit_values, regular_values = main_values.split('\n\n')

        return regular_values, slinit_values

