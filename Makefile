THEME=hugo-primer

default: preview

preview:
	hugo server -D true -vw -t $(THEME)

init:
	git submodule update --init --recursive
	git pull --recurse-submodules

.PHONY: preview init
