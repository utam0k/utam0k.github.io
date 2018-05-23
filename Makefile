BLOG_PATH=public
THEME=capsule

SOURCE_ORIGIN=git@github.com:utam0k/utam0k.github.io.git
BLOG_ORIGIN=$(SOURCE_ORIGIN)

default: preview

preview:
	hugo server -Dtrue -vw -t $(THEME)

build:
	hugo -v

deploy:
	hugo -v
	git add public
	git commit -m "Updated at `date '+%Y-%m-%d %H:%M:%S UTC'`"
	git subtree push -P $(BLOG_PATH) $(BLOG_ORIGIN) master

.PHONY: preview build deploy dry push_theme
