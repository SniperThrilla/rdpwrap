VENV := venv
PIP := $(VENV)/bin/pip

build:
	$(PIP) install -r requirements.txt
	pyinstaller --onefile --manifest resources/admin.manifest --paths src --add-data "resources:resources" --add-data "bin:bin" --name RDPPatcher --uac-admin --windowed src/rdppatcher/__main__.py

$(VENV):
	python3 -m venv $(VENV)

clean:
	rm -rf build dist *.spec
