#!/bin/bash
set -e

echo "Setting up Advanced Prompt Engineering Orchestration System..."

# Create virtual environment
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create data directories
mkdir -p data/vector_db
mkdir -p data/long_term
mkdir -p data/state
mkdir -p logs

# Copy environment file if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template. Please edit it with your API keys."
fi

# Initialize the system
python -c "from config.settings import get_settings; print('Settings loaded successfully'); print('Environment:', get_settings().environment)"

echo ""
echo "Setup complete!"
echo ""
echo "To start the server:"
echo "  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "Or for development with auto-reload:"
echo "  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
