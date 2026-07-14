#!/usr/bin/env bash

# exit on error
set -o errexit

# set the django settings module
export DJANGO_SETTINGS_MODULE=idmypill_spl.settings_production

# set the location of the 'data' directory containing datasets,
# co-occurrence matrix, etc.
export IDMYPILL_DATA_DIR="/var/idmypill-data/data/"

# delete the original 'data' directory in the repo, then create a
# sym-link to the new one
rm -rf data
ln -s $IDMYPILL_DATA_DIR data

# install dependencies
echo "Installing python dependencies"
pip install -U pip
pip install -r requirements.txt

# build the static files
echo "Collecting staticfiles"
python manage.py collectstatic --noinput

# run any database migrations
echo "Running database migrations"
python manage.py migrate
