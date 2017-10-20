RPYTHON=../3rd/pypy/rpython/bin/rpython

labels:
	gcc -Wall src/benchmark/labels.c -o bin/benchmark-labels

bin/benchmark-threaded: src/benchmark/threaded.py
	python ${RPYTHON} --log --output=bin/benchmark-threaded src/benchmark/threaded.py

bin/benchmark-ast: src/benchmark/ast.py
	python ${RPYTHON} --log --output=bin/benchmark-ast src/benchmark/ast.py

ITERATIONS=1000000000
benchmark:
	time bin/benchmark-labels ${ITERATIONS}
	time bin/benchmark-threaded ${ITERATIONS}
	time bin/benchmark-ast ${ITERATIONS}