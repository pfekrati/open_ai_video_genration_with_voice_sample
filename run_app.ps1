Write-Host "Setting up AI Teaser Video Generator..." -ForegroundColor Green

# Run setup script
python setup.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Setup failed. Please check the errors above." -ForegroundColor Red
    Read-Host -Prompt "Press Enter to exit"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Starting the application..." -ForegroundColor Green
Write-Host ""

# Run the Streamlit app
streamlit run app.py

Read-Host -Prompt "Press Enter to exit"
