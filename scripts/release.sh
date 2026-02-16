#!/bin/bash

# ResumePilot Release Wrapper
# Usage: ./scripts/release.sh [arguments passed to release.py]
# Example: ./scripts/release.sh --type resume

# Ensure we are in the project root
if [ ! -d "scripts" ]; then
    echo "❌ Error: Please run this script from the project root."
    echo "Usage: ./scripts/release.sh ..."
    exit 1
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Setting it up..."
    ./scripts/setup_env.sh
fi

# Activate virtual environment
source venv/bin/activate

# Run release.py with all passed arguments
python3 scripts/release.py "$@"

# Deactivate venv (optional, but good practice if sourced, ensuring clean exit)
deactivate
