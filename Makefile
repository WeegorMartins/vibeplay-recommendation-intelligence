.PHONY: install data validate train test serve api all

install:
	pip install -r requirements.txt

data:
	python -m src.generate_data --output data/raw

validate:
	python scripts/validate_data.py

train:
	python -m src.pipeline --data data/raw --artifacts artifacts --dashboard dashboard

test:
	python -m pytest -q

serve:
	python -m http.server 8000 --directory dashboard

api:
	python -m uvicorn api.app:app --reload --port 8001

all: data validate train test
