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
	PYTHONPATH=. python ${RPYTHON} --log --opt=jit --output=$@ $<
.PHONY: bin/meta

run: bin/meta
	PYPYLOG=jit:meta.log $<

disassemble: meta.log
	PYTHONPATH=3rd/pypy 3rd/pypy/rpython/jit/backend/tool/viewcode.py meta.log
	# note: his requires `dot` from graphviz (e.g. dnf install graphviz) and pygame (e.g. pip install pygame)
