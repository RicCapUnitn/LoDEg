SHELL=/bin/sh #Shell da utilizzare per l'esecuzione dei comandi

to_web:
	./tools/lib_to_web

from_web:
	./tools/web_to_lib

#target "clean" non è un file!
.PHONY: clean