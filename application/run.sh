#!/bin/bash
# run.sh

# Set environment variables
export DJANGO_SETTINGS_MODULE=application.settings
export PYTHONPATH=/home/momoyvan/Desktop/project/MentalApp/application

# Run Daphne
daphne application.asgi:application --port 8000