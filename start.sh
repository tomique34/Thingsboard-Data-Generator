#!/bin/bash

# Determine if we're running in production mode (like Docker) or development
if [ "$FLASK_DEBUG" = "True" ] || [ "$FLASK_DEBUG" = "true" ]; then
    echo "Starting in DEBUG mode..."
    python app.py
else
    echo "Starting in PRODUCTION mode..."
    gunicorn --bind 0.0.0.0:5001 --workers 2 app:app
fi
