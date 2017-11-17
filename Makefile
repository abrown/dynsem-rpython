RPYTHON=3rd/pypy/rpython/bin/rpython

# define FAST=1 to avoid the long-compiling JIT option
ifeq (${FAST}, undefined)
JIT_OPT:=jit
else
JIT_OPT:=3
endif

all: test

3rd:
	git submodule init
	git submodule update
.PHONY: 3rd

test:
	python -m unittest discover -s src/meta/test -p "*.py" -t .

bin/e2: src/main/e2.py $(shell find src/meta/*.py)
	mkdir -p bin
	PYTHONPATH=. python ${RPYTHON} --log --opt=${JIT_OPT} --output=$@ $<

bin/while: src/main/while.py $(shell find src/meta/*.py)
	mkdir -p bin
	PYTHONPATH=. python ${RPYTHON} --log --opt=${JIT_OPT} --output=$@ $<

run: bin/e2
	PYPYLOG=jit:e2.log $< src/main/sumprimes.e2

disassemble: e2.log
	PYTHONPATH=3rd/pypy 3rd/pypy/rpython/jit/backend/tool/viewcode.py $<
	# note: his requires `dot` from graphviz (e.g. dnf install graphviz) and pygame (e.g. pip install pygame)

clean:
	rm -rf bin
