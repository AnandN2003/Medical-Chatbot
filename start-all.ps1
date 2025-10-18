# Medical Chatbot - Start Both Servers
# This script starts both backend and frontend in separate windows

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Medical Chatbot - Starting Development Servers" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = "d:\anand\Medical Chatbot\Medical-Chatbot"

# Check if .env file exists
$envPath = Join-Path $rootPath "backend\.env"
if (-not (Test-Path $envPath)) {
    Write-Host "⚠️  ERROR: .env file not found in backend folder!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create a .env file with your API keys:" -ForegroundColor Yellow
    Write-Host "  1. Go to: backend\" -ForegroundColor Yellow
    Write-Host "  2. Copy .env.example to .env" -ForegroundColor Yellow
    Write-Host "  3. Add your PINECONE_API_KEY and GEMINI_API_KEY" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "✅ Found .env file" -ForegroundColor Green
Write-Host ""

# Start Backend Server
Write-Host "🚀 Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootPath\backend'; Write-Host '============================================================' -ForegroundColor Cyan; Write-Host '  Backend Server - Port 8000' -ForegroundColor Cyan; Write-Host '============================================================' -ForegroundColor Cyan; Write-Host ''; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 2

# Start Frontend Server
Write-Host "🚀 Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootPath\frontend'; Write-Host '============================================================' -ForegroundColor Cyan; Write-Host '  Frontend Server - Port 5173' -ForegroundColor Cyan; Write-Host '============================================================' -ForegroundColor Cyan; Write-Host ''; npm run dev"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  ✅ Both servers are starting!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Backend:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🌐 Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Keep both terminal windows open while using the app" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
