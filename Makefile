# PyTUI - run tests with conda pytui environment
.PHONY: test test-core test-unit

test:
	conda run -n pytui python -m pytest tests/unit/ -v --tb=short

test-core:
	conda run -n pytui python -m pytest tests/unit/core/ -v --tb=short

test-unit:
	conda run -n pytui python -m pytest tests/unit/ -v --tb=short
