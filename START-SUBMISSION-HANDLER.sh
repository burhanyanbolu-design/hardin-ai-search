#!/bin/bash

# Start Submission Handler on AWS Ubuntu
# Run this on your AWS server

echo "🚀 Starting Hardin Submission Handler..."
echo "📍 Server: 3.11.229.68:5001"
echo ""

# Navigate to project directory
cd ~/hardin-ai-search 2>/dev/null || cd ~/Desktop/SmartTracker-AI/ai-search-engine 2>/dev/null || cd .

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "💡 Create .env with your GitHub token for better rate limits"
fi

# Start the submission handler
echo ""
echo "🎯 Starting submission handler..."
echo "🔗 Endpoint: http://3.11.229.68:5001/api/submit"
echo "💡 Press Ctrl+C to stop"
echo ""

python3 submission_handler.py
