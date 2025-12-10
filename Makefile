THEME=utam0k
EDITOR ?= vim

default: preview

preview:
	hugo server -D -w -t $(THEME) --config config.yaml,config.dev.yaml --baseURL http://localhost:1313/

.PHONY: preview init tmp check

init:
	git submodule update --init --recursive
	git pull --recurse-submodules

tmp:
	$(eval FILENAME := $(shell date +%Y%m%d%H%M%S))
	hugo new tmp/$(FILENAME).md --kind tmp
	$(EDITOR) content/tmp/$(FILENAME).md

check:
	@command -v mise >/dev/null 2>&1 || { echo "mise is required for make check" >&2; exit 2; }
	mise exec uv -- uv run --quiet --with pillow ./hack/check_ogp_overflow.py
