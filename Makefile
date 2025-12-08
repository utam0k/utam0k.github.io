THEME=utam0k
EDITOR ?= vim

default: preview

preview:
	hugo server -D -w -t $(THEME) --config config.yaml,config.dev.yaml --baseURL http://localhost:1313/

init:
	git submodule update --init --recursive
	git pull --recurse-submodules

tmp:
	$(eval FILENAME := $(shell date +%Y%m%d%H%M%S))
	hugo new tmp/$(FILENAME).md --kind tmp
	$(EDITOR) content/tmp/$(FILENAME).md
