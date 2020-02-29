fix: black isort
check: black-check flake isort-check

black:
	black . --config black.toml

black-check:
	black . --config black.toml --check

flake:
	flake8 --config=setup.cfg --exit-zero

isort:
	isort -rc .

isort-check:
	isort -rc --check-only .
