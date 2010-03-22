# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = 
SPHINXBUILD   ?= ./sphinx_build
SPHINXAUTOGEN   ?= ./sphinx_autogen
SPHINXAUTOGENPOST ?= ./sphinx_autogen_postprocess
PAPER         =

# Internal variables.
PAPEROPT_a4     ?= -D latex_paper_size=a4
PAPEROPT_letter ?= -D latex_paper_size=letter
ALLSPHINXOPTS   ?= -d build/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) source
EPYTARGET       ?= build/html/generated/api
AUTOGEN_TARGET  ?= source/generated
PY_IMPORT_BASE	?= mrv


.PHONY: help clean html web pickle htmlhelp latex changes linkcheck epydoc autogen

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  pickle    to make pickle files (usable by e.g. sphinx-web)"
	@echo "  htmlhelp  to make HTML files and a HTML help project"
	@echo "  latex     to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  changes   to make an overview over all changed/added/deprecated items"
	@echo "  linkcheck to check all external links for integrity"

clean:
	-rm -rf build/*
	-rm -rf $(AUTOGEN_TARGET)
	-rm source/index.rst

source/index.rst:
	@echo Generating $@
	@find ../ -name "*.py" -not -wholename "*/test/*" \
	-not -wholename "*/start/*" -not -wholename "*/ext/*" \
	-not -wholename "*/doc/*" -not -name "__init__.py" | \
	sort | sed "s#^../#\\t$(PY_IMPORT_BASE)/#" | sed "s#.py\$$##" | sed "s#/#.#g" > $(@).center
	@cat $(@).header $(@).center $(@).footer > $@
	@rm $(@).center
	
epydoc:
	@mkdir -p $(EPYTARGET)
	./epydoc -q -q -o $(EPYTARGET)

autogen: source/index.rst
	-rm $(AUTOGEN_TARGET)/*
	$(SPHINXAUTOGEN) -o $(AUTOGEN_TARGET) $^
	$(SPHINXAUTOGENPOST) $(AUTOGEN_TARGET)
	
	
html: source/index.rst autogen epydoc
	@mkdir -p build/html build/doctrees
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) build/html
	@echo
	@echo "Build finished. The HTML pages are in build/html."

full: html

rebuild: clean full

pickle: source/index.rst
	mkdir -p build/pickle build/doctrees
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) build/pickle
	@echo
	@echo "Build finished; now you can process the pickle files or run"
	@echo "  sphinx-web build/pickle"
	@echo "to start the sphinx-web server."

web: pickle

htmlhelp: source/index.rst
	mkdir -p build/htmlhelp build/doctrees
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) build/htmlhelp
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in build/htmlhelp."

latex: source/index.rst
	mkdir -p build/latex build/doctrees
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) build/latex
	@echo
	@echo "Build finished; the LaTeX files are in build/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

changes: source/index.rst
	mkdir -p build/changes build/doctrees
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) build/changes
	@echo
	@echo "The overview file is in build/changes."

linkcheck: source/index.rst
	mkdir -p build/linkcheck build/doctrees
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) build/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in build/linkcheck/output.txt."
