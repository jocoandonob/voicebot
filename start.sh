#!/bin/bash

# Create required directories if they don't exist
mkdir -p app/static/uploads app/static/audio app/templates

# Run the FastAPI application
python run.py