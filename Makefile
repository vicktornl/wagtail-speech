default: clean format install

clean:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +

format:
	black src
	isort src

install:
	pip install -e .[test]

test:
	py.test tests

wheel:
	rm -rf dist/
	pip install wheel
	python setup.py sdist bdist_wheel
