RPYTHON=3rd/pypy/rpython/bin/rpython
VERSION=0.1
IMAGE=dynsem:${VERSION}

# define FAST=1 to avoid the long-compiling JIT option
ifeq (${FAST}, )
JIT_OPT:=jit
else
JIT_OPT:=3
endif

# setup proxy for Docker
ifeq (${http_proxy}, )
PROXY:=
else
PROXY:=--build-arg http_proxy=${http_proxy} --build-arg https_proxy=${https_proxy}
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

E2_LOG=e2-$(shell date +%s).log
run: bin/e2
	PYPYLOG=jit:${E2_LOG} time $< src/main/sumprimes.e2

show-last-log:
	less $(shell ls e2-*.log | tail -n 1)

disassemble: e2.log
	PYTHONPATH=3rd/pypy 3rd/pypy/rpython/jit/backend/tool/viewcode.py $<
	# note: his requires `dot` from graphviz (e.g. dnf install graphviz) and pygame (e.g. pip install pygame)

docker: Dockerfile $(shell find src/meta/*.py)
	docker build ${PROXY} --tag ${IMAGE} .

docker-run: docker
	docker run -it --rm ${IMAGE}

clean:
	rm *.log
	rm -rf bin
	docker rmi ${IMAGE}
