#!/bin/bash

source venv/bin/activate
while true; do
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo "Deploy command failed, retrying in 3 secs..."
    sleep 3
done
flask translate compile
exec gunicorn -b :5000 --access-logfile - --error-logfile - run:app
