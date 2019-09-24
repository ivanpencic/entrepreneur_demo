#!/bin/bash
NOW=$(date +"%d_%m_%Y")
pipenv run python manage.py dumpdata --natural-foreign --natural-primary > "db_dumps/dump_$NOW.json"

