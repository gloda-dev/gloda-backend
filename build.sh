#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r src/requirements.txt

cd src

python manage.py collectstatic --no-input
python manage.py migrate
