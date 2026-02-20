# Test Protected Endpoints
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Testing Protected Endpoints" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# First, get a token
Write-Host "1. Getting authentication token..." -ForegroundColor Yellow
$loginBody = @{
    email = "dr.johnson@abena.com"
    password = "Abena2024Secure"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:4002/api/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "✅ Token obtained: $($token.Substring(0, 50))..." -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test health endpoint (should work without auth)
Write-Host "2. Testing /health endpoint (no auth required)..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:4002/health" -Method Get
    Write-Host "✅ Health check successful" -ForegroundColor Green
    Write-Host "   Status: $($healthResponse.status)" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test /api/v1/doctors endpoint (should work without auth based on code)
Write-Host "3. Testing /api/v1/doctors endpoint..." -ForegroundColor Yellow
try {
    $doctorsResponse = Invoke-RestMethod -Uri "http://localhost:4002/api/v1/doctors" -Method Get
    Write-Host "✅ Doctors endpoint accessible" -ForegroundColor Green
    Write-Host "   Found $($doctorsResponse.Count) doctors" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "⚠️  Doctors endpoint: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
}

# Test with JWT token in header
Write-Host "4. Testing endpoint with JWT token..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

try {
    # Try accessing doctors endpoint with token
    $doctorsWithAuth = Invoke-RestMethod -Uri "http://localhost:4002/api/v1/doctors" -Method Get -Headers $headers
    Write-Host "✅ Endpoint accessible with JWT token" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "⚠️  Endpoint with auth: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
}

# Test invalid token
Write-Host "5. Testing with invalid token..." -ForegroundColor Yellow
$invalidHeaders = @{
    "Authorization" = "Bearer invalid_token_here"
    "Content-Type" = "application/json"
}

try {
    $invalidResponse = Invoke-RestMethod -Uri "http://localhost:4002/api/v1/doctors" -Method Get -Headers $invalidHeaders
    Write-Host "⚠️  Invalid token was accepted (should be rejected)" -ForegroundColor Yellow
    Write-Host ""
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✅ Invalid token correctly rejected (401 Unauthorized)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Unexpected error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Test rate limiting (make multiple rapid requests)
Write-Host "6. Testing rate limiting (10 rapid requests)..." -ForegroundColor Yellow
$successCount = 0
$rateLimitCount = 0
for ($i = 1; $i -le 10; $i++) {
    try {
        $rateTestResponse = Invoke-RestMethod -Uri "http://localhost:4002/api/v1/doctors" -Method Get -Headers $headers -ErrorAction Stop
        $successCount++
    } catch {
        if ($_.Exception.Response.StatusCode -eq 429) {
            $rateLimitCount++
            Write-Host "   Request $i : Rate limited (429)" -ForegroundColor Yellow
        } else {
            Write-Host "   Request $i : Error - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Start-Sleep -Milliseconds 100
}
Write-Host "   Successful: $successCount, Rate Limited: $rateLimitCount" -ForegroundColor Cyan
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Protected Endpoints Testing Complete" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

