#!/bin/bash

echo "Graph Analysis AI - Setup and Start Script"
echo "==========================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists python; then
    echo "❌ Python is not installed. Please install Python 3.8+"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

if ! command_exists psql; then
    echo "❌ PostgreSQL client is not installed. Please install PostgreSQL"
    exit 1
fi

echo "✅ All prerequisites are installed"

# Setup backend
echo ""
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your Gemini API key and database URL"
fi

cd ..

# Setup frontend
echo ""
echo "Setting up frontend..."
cd frontend

echo "Installing Node.js dependencies..."
npm install

if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    cp .env.local.example .env.local
fi

cd ..

# Database setup
echo ""
echo "Database setup..."
echo "Please make sure PostgreSQL is running and execute:"
echo "  createdb graph_analysis"
echo "  psql -d graph_analysis -f database/init.sql"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "1. Start the backend: cd backend && python main.py"
echo "2. Start the frontend: cd frontend && npm run dev"
echo "3. Open http://localhost:3000 in your browser"
