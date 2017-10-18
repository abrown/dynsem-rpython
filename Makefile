RPYTHON=3rd/pypy/rpython/bin/rpython

all: test

3rd:
	git submodule init
	git submodule update
.PHONY: 3rd

test:
	python -m unittest discover -s src/meta/test -p "*.py" -t .

bin/meta: src/meta/rpythonized.py
	python ${RPYTHON} --log --output=$@ $<
