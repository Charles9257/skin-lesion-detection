#!/bin/bash

# Railway startup script
echo "Starting Railway deployment..."

# Set production environment variables
export DEBUG=False
export DJANGO_SETTINGS_MODULE=backend.settings

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Create superuser automatically
echo "Creating admin user..."
python create_admin.py

# Start the server
echo "Starting Django server..."
port=${PORT:-8000}
echo "Using port: $port"
gunicorn backend.wsgi:application --bind 0.0.0.0:$port --workers 2