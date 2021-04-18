#!/bin/bash

if [[ "$ENV" == prod* ]]; then
	git pull
fi
python -m venv .venv
./.venv/bin/pip install -r requirements.txt

./.venv/bin/python -m artbot
