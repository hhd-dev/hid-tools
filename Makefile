all: doc test man

man_pages = $(patsubst %.md,%.1,$(wildcard man/*.md))
pytest3 = $(shell command -v pytest-3 pytest | head -n1)

%.1 : %.md
	pandoc  -s -t man -f markdown $< > $@

man: $(man_pages)

doc:
	sphinx-apidoc -f -e -o doc/source . setup.py tests/conftest.py
	sphinx-build -a -b html doc/source doc/html

test:
	sudo $(pytest3)

clean:
	rm -rf doc/html
	rm -rf man/*.1

.PHONY: doc test
