#!/bin/bash

# Setup Python Virtual Environment

# 1. Check if python3 is available
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 could not be found."
    exit 1
fi

# 2. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found. Skipping dependency installation."
fi

echo "✅ Setup complete. To activate the virtual environment, run:"
echo "source venv/bin/activate"
