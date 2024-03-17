install: lint
	python3 setup.py install --user

lint:
	ruff check taskrun/

format:
	black taskrun/