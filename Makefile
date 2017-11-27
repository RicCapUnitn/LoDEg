SHELL=/bin/sh #Shell da utilizzare per l'esecuzione dei comandi

PORT = 8000

clean:
	./tools/clean.sh

website:
	cd src/lodeg_website; python manage.py runserver $(PORT)

to_web:
	./tools/lib_to_web.sh

from_web:
	./tools/web_to_lib.sh

#target "clean" non è un file!
.PHONY: clean