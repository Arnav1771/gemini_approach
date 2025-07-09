@echo off
echo Graph Analysis AI - Setup and Start Script
echo ===========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+
    pause
    exit /b 1
)

echo ✅ All prerequisites are installed

REM Setup backend
echo.
echo Setting up backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit backend\.env with your Gemini API key and database URL
)

cd ..

REM Setup frontend
echo.
echo Setting up frontend...
cd frontend

echo Installing Node.js dependencies...
npm install

if not exist ".env.local" (
    echo Creating .env.local file...
    copy .env.local.example .env.local
)

cd ..

REM Database setup
echo.
echo Database setup...
echo Please make sure PostgreSQL is running and execute:
echo   createdb graph_analysis
echo   psql -d graph_analysis -f database\init.sql

echo.
echo 🎉 Setup complete!
echo.
echo To start the application:
echo 1. Start the backend: cd backend ^&^& python main.py
echo 2. Start the frontend: cd frontend ^&^& npm run dev
echo 3. Open http://localhost:3000 in your browser

pause
