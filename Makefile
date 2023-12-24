ifeq ($(OS),Windows_NT)
	INSTALLER := pyinstaller.exe
	SPECOPTS := -w -i icon.ico --add-binary icon.ico:.
	HAS_SPLASH := yes
else
	UNAME = $(shell uname -s)
	INSTALLER := pyinstaller
	ifeq ($(UNAME),Darwin)
		SPECOPTS := --strip --add-binary icon.png:. -w -i icon.png
		HAS_SPLASH := no
	else
		SPECOPTS := --add-binary icon.png:.
		HAS_SPLASH := yes
	endif
endif

ifeq ($(HAS_SPLASH),yes)
	SPLASH := --splash splash.png
endif

NAME := "PDF Concatenator 2000 Pro"
OPTIONS := --clean -y -D -n $(NAME) --contents-directory .

.PHONY: clean

pdfconcat: pdfconcat.py
	$(INSTALLER) $(OPTIONS) $(SPECOPTS) $(SPLASH) $<

clean:
	rm -rf dist build
