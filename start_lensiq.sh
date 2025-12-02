#!/bin/bash

# LensIQ Data Ingestion & TrendRadar Startup Script
# Branch: LensIQ_DataIngestion_TrendRadar

echo "🚀 Starting LensIQ Data Ingestion & TrendRadar..."
echo ""

# Set Python path
export PYTHONPATH=/Users/danieldeenik/Documents/GitHub/TrendSense

# Activate virtual environment
source venv/bin/activate

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB is not running. Starting MongoDB..."
    mongod --dbpath /usr/local/var/mongodb --logpath /usr/local/var/log/mongodb/mongo.log --fork
    sleep 2
fi

# Start Flask application
echo "✅ Starting Flask application..."
echo "📍 TrendRadar will be available at: http://localhost:5050/trends"
echo ""

python3 app.py

