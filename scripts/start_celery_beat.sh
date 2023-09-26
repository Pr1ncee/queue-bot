#!/bin/bash

export PYTHONPATH="${PYTHONPATH}:/app"

cd /app/

python -m celery -A celery_app beat -l info
