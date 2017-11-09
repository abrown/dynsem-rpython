RPYTHON=3rd/pypy/rpython/bin/rpython

all: test

3rd:
	git submodule init
	git submodule update
.PHONY: 3rd

test:
	python -m unittest discover -s src/meta/test -p "*.py" -t .

bin/e2: src/main/e2.py
	mkdir -p bin
	PYTHONPATH=. python ${RPYTHON} --log --opt=jit --output=$@ $<
.PHONY: bin/meta

bin/while: src/main/while.py
	mkdir -p bin
	PYTHONPATH=. python ${RPYTHON} --log --opt=jit --output=$@ $<
.PHONY: bin/meta

run: bin/while
	PYPYLOG=jit:while.log $<

disassemble: while.log
	PYTHONPATH=3rd/pypy 3rd/pypy/rpython/jit/backend/tool/viewcode.py meta.log
	# note: his requires `dot` from graphviz (e.g. dnf install graphviz) and pygame (e.g. pip install pygame)
