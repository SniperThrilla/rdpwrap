VENV := venv
PIP := $(VENV)/bin/pip

.PHONY: venv

build: $(VENV)
	$(PIP) install -r requirements.txt
	$(VENV)/bin/pyinstaller --onefile --manifest resources/admin.manifest --paths src --add-data "resources:resources" --add-data "bin:bin" --name RDPPatcher --uac-admin --windowed src/rdppatcher/__main__.py

$(VENV):
	python3 -m venv $(VENV)
	. $(VENV)/bin/activate

clean:
	rm -rf build dist *.spec
