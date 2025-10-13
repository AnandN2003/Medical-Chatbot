# Quick Test Script for Backend API
# Run this after starting the server to test the endpoints

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🧪 Testing Medical Chatbot Backend API" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"

# Test 1: Root endpoint
Write-Host "📍 Test 1: Root Endpoint" -ForegroundColor Green
Write-Host "   GET $baseUrl/" -ForegroundColor Gray
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "   ✅ Success!" -ForegroundColor Green
    $response | ConvertTo-Json | Write-Host
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Health check
Write-Host "📍 Test 2: Health Check" -ForegroundColor Green
Write-Host "   GET $baseUrl/api/v1/health" -ForegroundColor Gray
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/health" -Method Get
    Write-Host "   ✅ Success!" -ForegroundColor Green
    $response | ConvertTo-Json | Write-Host
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Readiness check
Write-Host "📍 Test 3: Readiness Check" -ForegroundColor Green
Write-Host "   GET $baseUrl/api/v1/ready" -ForegroundColor Gray
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/ready" -Method Get
    Write-Host "   ✅ Success!" -ForegroundColor Green
    $response | ConvertTo-Json | Write-Host
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Chat query
Write-Host "📍 Test 4: Chat Query" -ForegroundColor Green
Write-Host "   POST $baseUrl/api/v1/chat/query" -ForegroundColor Gray
$body = @{
    question = "What is diabetes?"
    top_k = 3
    return_sources = $true
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/chat/query" -Method Post -Body $body -ContentType "application/json"
    Write-Host "   ✅ Success!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Question: What is diabetes?" -ForegroundColor Cyan
    Write-Host "   Answer: $($response.answer)" -ForegroundColor White
    Write-Host "   Sources: $($response.sources -join ', ')" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✅ Testing Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
