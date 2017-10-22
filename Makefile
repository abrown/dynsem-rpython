RPYTHON=3rd/pypy/rpython/bin/rpython

all: test

3rd:
	git submodule init
	git submodule update
.PHONY: 3rd

test:
	python -m unittest discover -s src/meta/test -p "*.py" -t .

bin/meta: src/meta/rpythonized.py
	mkdir -p bin
	PYTHONPATH=. python ${RPYTHON} --log --output=$@ $<
.PHONY: bin/meta
