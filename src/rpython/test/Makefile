PYPY=../../../3rd/pypy

all: test

test:
	python ${PYPY}/pytest.py *.py

clean: clean-pyc
PHONY: clean

clean-pyc:
	rm -f *.pyc
PHONY: clean-pyc
