all: doc test man

man_pages = $(patsubst %.md,%.1,$(wildcard man/*.md))
pytest3 = $(shell command -v pytest-3 pytest | head -n1)

%.1 : %.md
	pandoc  -s -t man -f markdown $< > $@

man: $(man_pages)

test:
	sudo $(pytest3)

clean:
	rm -rf man/*.1

.PHONY: doc test
