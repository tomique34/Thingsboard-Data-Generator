@echo off
REM Setup script for Thingsboard Data Generator on Windows

echo Setting up Thingsboard Data Generator...

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete! To start the application:
echo 1. Activate the virtual environment: venv\Scripts\activate
echo 2. Run the application: python app.py
echo 3. Access the web interface at http://localhost:5001
echo.
echo Make sure to configure your Thingsboard connection details in the .env file.
pause
