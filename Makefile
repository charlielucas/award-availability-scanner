PYTHON ?= python3

.PHONY: test demo

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests

demo:
	PYTHONPATH=src $(PYTHON) -m award_availability --input data/sample_search_response.json --origin AAA --destination BBB --outdir examples
