ifeq ($(OS),Windows_NT)
	INSTALLER := pyinstaller.exe
	OPTIONS := --onefile -w -i icon.ico
else
	UNAME = $(shell uname -s)
	INSTALLER := pyinstaller
	ifeq ($(UNAME),Darwin)
		OPTIONS := --onedir --strip -w -i icon.png
	endif
endif

NAME := "PDF Concatenator 2000 Pro"
OPTIONS += --clean -y -n $(NAME) --contents-directory .

.PHONY: clean

pdfconcat: pdfconcat.py rc_static.py
	$(INSTALLER) $(OPTIONS) $<

rc_static.py: static.qrc backdrop.png icon.png
	pyside6-rcc static.qrc -o rc_static.py

icon.ico: icon.png
	magick icon.png -resize 64x64 icon.ico

clean:
	rm -rf dist build
