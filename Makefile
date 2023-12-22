# alternative: MACHINE
ifdef COMSPEC
	INSTALLER := pyinstaller.exe
	SPECOPTS := -w -i icon.ico --add-binary icon.ico:.
else
	INSTALLER := pyinstaller
	SPECOPTS := --strip --add-binary icon.png:.
endif

NAME := "PDF Concatenator 2000 Pro"
OPTIONS := --clean -y -D -n $(NAME) --contents-directory . --splash splash.png

.PHONY: clean

pdfconcat: pdfconcat.py
	$(INSTALLER) $(OPTIONS) $(SPECOPTS) $<

clean:
	rm -rf dist build
