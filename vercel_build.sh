#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p api

# Copy app.py to api/
cp app.py api/
cp -r static/ api/ || true
cp -r templates/ api/ || true

# Install psycopg2 dependencies
yum install -y postgresql-devel

# Install Python dependencies
pip install psycopg2-binary

# Set execute permissions
chmod +x vercel_build.sh
