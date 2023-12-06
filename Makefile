pdfconcat: pdfconcat.py
	pyinstaller --clean -F -n "PDF Concatenator 2000 Pro" --add-data icon.png:. -w -i icon.ico $<