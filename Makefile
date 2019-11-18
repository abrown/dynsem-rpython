
# default target
all: test


#
# SETUP
# Fetch pypy's source to use for compiling RPython programs
#
3rd:
	git submodule update --init --recursive
.PHONY: 3rd


#
# TEST
#
test:
	python -m unittest discover -s src/meta/test -p "*.py" -t .
	python -m unittest discover -s src/compile/test -p "*.py" -t .


#
# BUILD
# Create all necessary binaries (and clean them up)
#
RPYTHON=3rd/pypy/rpython/bin/rpython

# define FAST=1 to avoid the long-compiling JIT option
ifeq (${FAST}, )
JIT_OPT:=jit
else
JIT_OPT:=3
endif

bin/e2: src/main/e2.py $(shell find src/meta/*.py)
	mkdir -p bin
	PYTHONPATH=. python ${RPYTHON} --log --opt=${JIT_OPT} --output=$@ $<

bin/e2-handmade: src/main/e2-handmade.py $(shell find src/compile/*.py) $(shell find src/meta/*.py)
	mkdir -p bin
	PYTHONPATH=. python ${RPYTHON} --log --opt=${JIT_OPT} --output=$@ $<

bin/while: src/main/while.py $(shell find src/meta/*.py) clean-pyc
	mkdir -p bin
	PYTHONPATH=. python ${RPYTHON} --log --opt=${JIT_OPT} --output=$@ $<

bin/while-c: src/main/while.c
	gcc -O0 $< -o $@

bin/sumprimes: src/main/sumprimes.c
	gcc -O0 $< -o $@

clean: clean-pyc
	rm -f *.log
	rm -rf bin
	docker rmi -f ${IMAGE}
PHONY: clean

clean-pyc:
	rm -f $(shell find src/**/*.pyc)
PHONY: clean-pyc


#
# RUN
# Execute binaries with a benchmark such as sumprimes
#
LOG=e2-$(shell date +%s).log

run: bin/e2
	PYPYLOG=jit:${LOG} time $< src/main/sumprimes.e2

run-handmade: bin/e2-handmade
	PYPYLOG=jit:${LOG} time $< src/main/sumprimes.e2

run-pypy: src/main/sumprimes.py
	PYPYLOG=jit:${LOG} time pypy $<

run-c: bin/sumprimes
	time bin/sumprimes

run-while: bin/e2
	PYPYLOG=jit:${LOG} time $< src/main/while.e2

run-while-pypy: src/main/while.py
	PYPYLOG=jit:${LOG} time pypy $<

run-while-handmade: bin/e2-handmade
	PYPYLOG=jit:${LOG} time $< src/main/while.e2

run-while-c: bin/while-c
	time $<

#
# BENCHMARK
# Execute the sumprime benchmark with all parameters
#
TIME:=/usr/bin/time
FORMAT:=
MAX_PRIMES:=1 10 100 1000 10000 100000
benchmark: bin/sumprimes src/main/sumprimes.py bin/e2-handmade src/main/sumprimes.e2
	@echo "[benchmark] & [max] & [total elapsed time] & [max resident memory]"
	@for MAX in ${MAX_PRIMES}; do \
		${TIME} -f "c & $$MAX & %E & %M" bin/sumprimes $$MAX > /dev/null; \
		sed "s/10000/$$MAX/" src/main/sumprimes.py | ${TIME} -f "pypy & $$MAX & %E & %M" pypy > /dev/null; \
		sed "s/10000/$$MAX/" src/main/sumprimes.e2 | ${TIME} -f "e2 & $$MAX & %E & %M" bin/e2-handmade > /dev/null; \
	done

ITERATIONS:=3
benchmark-accurate: bin/sumprimes src/main/sumprimes.py bin/e2-handmade src/main/sumprimes.e2
	@for MAX in ${MAX_PRIMES}; do \
		perf stat -r ${ITERATIONS} -d bin/sumprimes $$MAX; \
		sed "s/10000/$$MAX/" src/main/sumprimes.py > bin/sumprimes-$$MAX.py; \
		perf stat -r ${ITERATIONS} -d pypy bin/sumprimes-$$MAX.py; \
		sed "s/10000/$$MAX/" src/main/sumprimes.e2 > bin/sumprimes-$$MAX.e2; \
		perf stat -r ${ITERATIONS} -d bin/e2-handmade bin/sumprimes-$$MAX.e2; \
	done


#
# UTILITY
# Helpful targets for common tasks such as manipulating log files
#
show-last-log:
	less -N $(shell ls e2-*.log | tail -n 1)

# e.g. `make extract-last-log PATTERN=jit-log-opt-loop`
extract-last-log:
	cat $(shell ls e2-*.log | tail -n 1) | node src/util/extract-log-section.js ${PATTERN}

disassemble: e2.log
	PYTHONPATH=3rd/pypy 3rd/pypy/rpython/jit/backend/tool/viewcode.py $<
	# note: his requires `dot` from graphviz (e.g. dnf install graphviz) and pygame (e.g. pip install pygame)

sync:
ifndef to
	$(error 'to' is undefined, e.g. make sync to=user@host:~/path/to/code)
endif
	rsync -Cra --out-format='[%t]--%n' --exclude="3rd" --exclude=".idea" --exclude=".git" --exclude="bin" --exclude="*.pyc" . ${to}
.PHONY: sync


#
# DOCKER
# Build Dockerized environment for building and executing the targets in this file
# (not strictly necessary but gives an idea of what dependencies are required)
#
VERSION=0.1
IMAGE=dynsem:${VERSION}

# setup proxy for Docker
ifeq (${http_proxy}, )
PROXY:=
else
PROXY:=--build-arg http_proxy=${http_proxy} --build-arg https_proxy=${https_proxy}
endif

docker: Dockerfile $(shell find src/meta/*.py)
	docker build ${PROXY} --tag ${IMAGE} .

docker-run: docker
	docker run -it --rm ${IMAGE}
