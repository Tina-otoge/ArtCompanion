#!/bin/bash

if [[ "$ENV" == prod* ]]; then
	git checkout .
	git pull
	rm -rf .venv
fi
python -m venv .venv
./.venv/bin/pip install -r requirements.txt

./.venv/bin/python -m artbot
