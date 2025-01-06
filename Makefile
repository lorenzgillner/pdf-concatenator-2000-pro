APPNAME := PDF Concatenator 2000 Pro
INSTALLER := pyinstaller
APPIMAGEC := appimagetool-x86_64.AppImage
OPTIONS := --clean -y -n "$(APPNAME)" -w --contents-directory .

ifeq ($(OS),Windows_NT)
	OPTIONS += --onefile -i icon.ico
else
	OPTIONS += --onedir --strip -i icon.png
endif

.PHONY: appimage clean

pdfconcat: pdfconcat.py rc_static.py
	$(INSTALLER) $(OPTIONS) $<

rc_static.py: static.qrc backdrop.png icon.png
	pyside6-rcc static.qrc -o rc_static.py

icon.ico: icon.png
	magick icon.png -resize 64x64 icon.ico

appimage: pdfconcat
	mkdir -p build/"$(APPNAME).AppDir"/usr/bin
	cp -r dist/"$(APPNAME)"/* build/"$(APPNAME).AppDir"/usr/bin/
	cp AppRun icon.png pdfconcat.desktop build/"$(APPNAME).AppDir"/
	$(APPIMAGEC) build/"$(APPNAME).AppDir" dist/"$(APPNAME).AppImage"

clean:
	rm -rf dist build rc_static.py
