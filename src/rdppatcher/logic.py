# logic.py

import subprocess
from PySide6.QtCore import QThread, Signal
import os, sys
from datetime import datetime
from pathlib import Path

RDP_FOLDER = r"C:\Program Files\RDP Wrapper"
INI_PATH = os.path.join(RDP_FOLDER, "rdpwrap.ini")
TERMSERVICE_STOPPED = 2

class Worker(QThread):
    log = Signal(str)
    done = Signal(bool)

    def __init__(self):
        super().__init__()
        self.last_process = [] 

    def run(self):
        self.log.emit("Disabling active RDP services...")
        result = self.run_program(["net", "stop", "TermService", "/y"])
        if result.returncode != 0 and result.returncode != TERMSERVICE_STOPPED:
            return self.fail(result)

        self.log.emit("Running Offset Finder...")
        offset_finder = self.bundled("bin/RDPWrapOffsetFinder.exe")
        result = self.run_program([offset_finder])
        if result.returncode != 0:
            return self.fail(result)

        self.log.emit("Creating rdpwrap.ini...")
        if not self.create_ini(result.stdout):
            return self.fail()

        self.log.emit("Re-enabling RDP services...")
        result = self.run_program(["net", "start", "TermService", "/y"])
        if result.returncode != 0:
            return self.fail(result)

        self.log.emit("Finished!")
        self.done.emit(True)

    def fail(self, result: subprocess.CompletedProcess = None):
        if result:
            self.debug_output(result)
        self.log.emit("An error has occurred...")
        self.done.emit(False)

    def bundled(self, path: str):
        base = getattr(sys, "_MEIPASS", os.path.abspath("."))
        return os.path.join(base, path)

    def run_program(self, args: list[str]):
        self.last_process = args
        return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    def debug_output(self, result: subprocess.CompletedProcess):
        self.log.emit(f"**FAILED** - {' '.join(self.last_process)} - Error Code: {result.returncode}")
        self.log.emit("STDOUT:")
        self.log.emit(result.stdout)
        self.log.emit("STDERR:")
        self.log.emit(result.stderr)

    def move_ini(self):
        if os.path.exists(INI_PATH):
            os.rename(INI_PATH, os.path.join(RDP_FOLDER, f"rdpwrap.ini.{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"))

    def create_ini(self, text: str):
        try:
            self.move_ini()
            template_path = self.bundled("resources/template.ini")
            template = Path(template_path).read_text()

            regular_values, slinit_values = self.process_output(text)
            template = template.format(regular_values=regular_values, slinit_values=slinit_values)

            p = Path(INI_PATH)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(template, encoding='utf-8')

            self.log.emit(f"New rdpwrap.ini written to {INI_PATH}")
            return True

        except Exception as e:
            self.log.emit(f"Unable to create new rdpwrap.ini: {e}")
            return False

    def process_output(self, main_values: str):
        main_values = main_values.replace("\r\n", "\n")
        slinit_values, regular_values = main_values.split('\n\n')

        return regular_values, slinit_values

