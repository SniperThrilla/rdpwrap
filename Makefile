build:
	pyinstaller --onefile --manifest resources/admin.manifest --paths src src/rdppatcher/__main__.py --add-data "resources/*:resources" --add-binary "bin/*:bin" --name RDPPatcher

clean:
	rm -rf build dist *.spec
