RPYTHON=../../3rd/pypy/rpython/bin/rpython


# test threaded implementations of dynsem-like transformations

labels: labels.c
	gcc -Wall $< -o $@

threaded: threaded.py
	python ${RPYTHON} --log --output=$@ $<

ast: ast.py
	python ${RPYTHON} --log --output=$@ $<

ITERATIONS=1000000000
benchmark:
	time ./labels ${ITERATIONS}
	time ./threaded ${ITERATIONS}
	time ./ast ${ITERATIONS}


# compare cost of method dynamic dispatch to switch statement

method: method.py
	PYTHONPATH=. python ${RPYTHON} --log --opt=jit --output=$@ $<

switch: switch.py
	PYTHONPATH=. python ${RPYTHON} --log --opt=jit --output=$@ $<

ITERATIONS=1000000000
run-calls: method switch
	PYPYLOG=jit:method.log time ./method ${ITERATIONS}
	PYPYLOG=jit:switch.log time ./switch ${ITERATIONS}

clean:
	rm *.pyc -f
	rm labels ast threaded method switch -f