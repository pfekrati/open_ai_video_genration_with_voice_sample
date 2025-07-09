@echo off
echo Setting up AI Teaser Video Generator...

REM Run setup script
python setup.py
if %errorlevel% neq 0 (
    echo Setup failed. Please check the errors above.
    pause
    exit /b %errorlevel%
)

echo.
echo Starting the application...
echo.

REM Run the Streamlit app
streamlit run app.py

pause
