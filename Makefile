.PHONY: check fmt test pkg-test

fmt:
	ruff format .
	ruff check --fix .
	pytest -q

check:
	ruff format --check .
	ruff check .
	pytest -q

test:
	pytest -q

pkg-test:
	rm -rf dist
	uv build --quiet
	uv pip install --python /tmp/cleanvenv/bin/python --reinstall --quiet dist/*.whl
	cd /tmp/faraway/site && /tmp/cleanvenv/bin/intaglio --vault /tmp/faraway/vault --force
