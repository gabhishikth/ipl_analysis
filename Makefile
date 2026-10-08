install:
	pip install -r requirements.txt
run:
	python scripts/run_pipeline.py
test:
	python -m pytest -q
clean-outputs:
	rm -f data/interim/*.csv data/processed/*.csv reports/tables/*.csv reports/figures/*.png
