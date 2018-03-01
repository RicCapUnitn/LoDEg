SHELL=/bin/sh #Shell da utilizzare per l'esecuzione dei comandi

# if set to @ will hide which command are executed,
# otherwise it will show all executed commands
SILENT = @
# if set to --silent will hide recursive make output,
# otherwise it will show all the outputs
MAKE_SILENT = --silent

RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
# turn args into do-nothing targets
$(eval $(RUN_ARGS):;@:)

help:
	$(SILENT)echo "LoDEg makefile\n"
	$(SILENT)echo "Rules:"
	$(SILENT)echo	"- help"
	$(SILENT)echo	"\t show this help"
	$(SILENT)echo	"- website PORT"
	$(SILENT)echo	"\t deploy the website"
	$(SILENT)echo	"- to_web"
	$(SILENT)echo	"\t copy WebApp library to standalone"
	$(SILENT)echo	"- from_web"
	$(SILENT)echo	"\t copy standalone library to WebApp"
	$(SILENT)echo	"- check"
	$(SILENT)echo	"\t check library integrity"
	$(SILENT)echo	"- tests [i,interactive]"
	$(SILENT)echo	"\t test the library"

website:
	$(SILENT)cd src/lodeg_website; python manage.py runserver $(filter-out $@, $(MAKECMDGOALS))

to_web: clean
	$(SILENT)echo ">>> Starting migration from the standalone library to the WebApp library..."
	$(SILENT)./tools/lib_to_web.sh
	$(SILENT)echo ">>> Done!\n"

from_web: clean
	$(SILENT)echo ">>> Starting migration from the WebApp library to the standalone library..."
	$(SILENT)./tools/web_to_lib.sh
	$(SILENT)echo ">>> Done!\n"

pep8_check:
	$(SILENT) pep8 .

pep8_reformat:
	$(SILENT) autopep8 --in-place --aggressive --experimental -r .

check: clean
	$(SILENT)echo ">>> Starting integrity test..."
	$(SILENT)./tools/check_migration.sh
	$(SILENT)echo ">>> Done!\n"

.SILENT: tests

requirements:
	$(SILENT)pipreqs --force --savepath ./requirements.txt ./src/lodegML

doc:
	$(SILENT)sphinx-apidoc -f -o docs/ src/lodegML/
	$(SILENT)cd docs/lodegML_docs && $(MAKE) html

tests:
	$(SILENT)echo ">>> Starting testing..."
	$(SILENT)./test/run_tests.sh $(filter-out $@, $(MAKECMDGOALS))
	$(SILENT)echo ">>> Done!\n"


### ===================== ###
###     Clean section     ###
### ===================== ###
# remove generated files
.PHONY: clean

clean:
	$(SILENT)echo ">>> Deleting temporary files..."
	$(SILENT)./tools/clean.sh
	$(SILENT)echo ">>> Done!\n"
