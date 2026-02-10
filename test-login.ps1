# Test Login Endpoint
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Testing Secure Login Endpoint" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Test Provider Login
Write-Host "Testing Provider Login..." -ForegroundColor Yellow
$providerBody = @{
    email = "dr.johnson@abena.com"
    password = "Abena2024Secure"
} | ConvertTo-Json

try {
    $providerResponse = Invoke-RestMethod -Uri "http://localhost:4002/api/v1/auth/login" -Method Post -Body $providerBody -ContentType "application/json"
    Write-Host "✅ Provider Login Successful!" -ForegroundColor Green
    Write-Host "Token: $($providerResponse.access_token.Substring(0, 50))..." -ForegroundColor Cyan
    Write-Host "User ID: $($providerResponse.user_id)" -ForegroundColor Cyan
    Write-Host "Role: $($providerResponse.role)" -ForegroundColor Cyan
    $global:providerToken = $providerResponse.access_token
    Write-Host ""
} catch {
    Write-Host "❌ Provider Login Failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Red
    }
    Write-Host ""
}

# Test Patient Login
Write-Host "Testing Patient Login..." -ForegroundColor Yellow
$patientBody = @{
    email = "john.doe@example.com"
    password = "Abena2024Secure"
} | ConvertTo-Json

try {
    $patientResponse = Invoke-RestMethod -Uri "http://localhost:4002/api/v1/auth/login" -Method Post -Body $patientBody -ContentType "application/json"
    Write-Host "✅ Patient Login Successful!" -ForegroundColor Green
    Write-Host "Token: $($patientResponse.access_token.Substring(0, 50))..." -ForegroundColor Cyan
    Write-Host "User ID: $($patientResponse.user_id)" -ForegroundColor Cyan
    Write-Host "Role: $($patientResponse.role)" -ForegroundColor Cyan
    $global:patientToken = $patientResponse.access_token
    Write-Host ""
} catch {
    Write-Host "❌ Patient Login Failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Login Testing Complete" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

