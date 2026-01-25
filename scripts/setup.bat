@echo off
echo Setting up Advanced Prompt Engineering Orchestration System...

REM Create virtual environment
if not exist venv (
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

REM Create data directories
if not exist data mkdir data
if not exist data\vector_db mkdir data\vector_db
if not exist data\long_term mkdir data\long_term
if not exist data\state mkdir data\state
if not exist logs mkdir logs

REM Copy environment file if not exists
if not exist .env (
    copy .env.example .env
    echo Created .env file from template. Please edit it with your API keys.
)

REM Initialize the system
python -c "from config.settings import get_settings; print('Settings loaded successfully'); print('Environment:', get_settings().environment)"

echo.
echo Setup complete!
echo.
echo To start the server:
echo   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo Or for development with auto-reload:
echo   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
