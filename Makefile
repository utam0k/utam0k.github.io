THEME=utam0k
HUGO_CACHEDIR ?= $(CURDIR)/.hugo_cache

default: preview

preview:
	HUGO_CACHEDIR=$(HUGO_CACHEDIR) hugo server -D -w -t $(THEME) --config config.yaml,config.dev.yaml --baseURL http://localhost:1313/

init:
	git submodule update --init --recursive
	git pull --recurse-submodules

.PHONY: preview init
