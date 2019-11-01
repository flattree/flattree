SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXAPIDOC  ?= sphinx-apidoc
SOURCEDIR     = source
BUILDDIR      = build
export SPHINX_APIDOC_OPTIONS=members
APIDOC_OPTS   = -d2 -e -P -M -H "API (sphinx-autodoc)"
APIDOC_OUTPUT = $(SOURCEDIR)/api
APIDOC_MODULE = ..
APIDOC_EXCLUDE = ../tests/* ../*.py
OPEN          = xdg-open

html:
	@rm -rf $(APIDOC_OUTPUT)/*
	@$(SPHINXAPIDOC) $(APIDOC_OPTS) -o "$(APIDOC_OUTPUT)" "$(APIDOC_MODULE)" $(APIDOC_EXCLUDE)
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	git add $(APIDOC_OUTPUT)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

view:
	@$(OPEN) $(BUILDDIR)/html/index.html

.PHONY: html Makefile view

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
