param(
  [string]$QuantumBaseUrl = "",
  [string]$PatientId = ""
)

$ErrorActionPreference = "Stop"

if (-not $QuantumBaseUrl) { $QuantumBaseUrl = $env:QUANTUM_BASE_URL }
if (-not $QuantumBaseUrl) { $QuantumBaseUrl = "https://abena-quantum-healthcare-platform.onrender.com" }

if (-not $PatientId) { $PatientId = $env:DEMO_PATIENT_ID }
if (-not $PatientId) { $PatientId = "JANE_001" }

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "ABENA Quantum Provider-Ordered Flow Test" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "QuantumBaseUrl: $QuantumBaseUrl" -ForegroundColor Gray
Write-Host "PatientId:      $PatientId" -ForegroundColor Gray
Write-Host ""

function Invoke-JsonPost($Url, $Body) {
  return Invoke-RestMethod -Uri $Url -Method Post -Body ($Body | ConvertTo-Json -Depth 10) -ContentType "application/json"
}

function Invoke-JsonGet($Url) {
  return Invoke-RestMethod -Uri $Url -Method Get
}

# 1) Patient submits intake request
Write-Host "1) Patient submits intake request..." -ForegroundColor Yellow
$createReq = Invoke-JsonPost "$QuantumBaseUrl/api/quantum-requests" @{
  patient_id  = $PatientId
  medications = @("Warfarin 5mg")
  supplements = @("Fish Oil 1000mg")
  conditions  = @("Type 2 Diabetes")
}

if (-not $createReq.success) { throw "Create request failed" }
$requestId = $createReq.request.request_id
Write-Host "✅ Created request: $requestId (status=$($createReq.request.status))" -ForegroundColor Green
Write-Host ""

# 2) Provider lists requests (should include the new one)
Write-Host "2) Provider lists requests..." -ForegroundColor Yellow
$listReq = Invoke-JsonGet "$QuantumBaseUrl/api/quantum-requests?patient_id=$([uri]::EscapeDataString($PatientId))"
$found = ($listReq.requests | Where-Object { $_.request_id -eq $requestId } | Select-Object -First 1)
if (-not $found) { throw "Provider list did not include request $requestId" }
Write-Host "✅ Provider sees request: $($found.request_id) (status=$($found.status))" -ForegroundColor Green
Write-Host ""

# 3) Provider orders request (generates results + IBM proof)
Write-Host "3) Provider orders the request..." -ForegroundColor Yellow
$ordered = Invoke-JsonPost "$QuantumBaseUrl/api/quantum-requests/$requestId/order" @{}
if (-not $ordered.success) { throw "Order failed" }
$jobId = $ordered.request.results.ibm_job.job_id
$backend = $ordered.request.results.ibm_job.backend
Write-Host "✅ Ordered. Status=$($ordered.request.status)" -ForegroundColor Green
Write-Host "   IBM Job ID: $jobId" -ForegroundColor Cyan
Write-Host "   Backend:    $backend" -ForegroundColor Cyan
Write-Host ""

# 4) Provider releases to patient
Write-Host "4) Provider releases results to patient..." -ForegroundColor Yellow
$released = Invoke-JsonPost "$QuantumBaseUrl/api/quantum-requests/$requestId/release" @{}
if (-not $released.success) { throw "Release failed" }
Write-Host "✅ Released. Status=$($released.request.status)" -ForegroundColor Green
Write-Host ""

# 5) Patient fetches released results
Write-Host "5) Patient fetches released results..." -ForegroundColor Yellow
$patientResults = Invoke-JsonGet "$QuantumBaseUrl/api/quantum-results?patient_id=$([uri]::EscapeDataString($PatientId))"
$match = ($patientResults.results | Where-Object { $_.request_id -eq $requestId } | Select-Object -First 1)
if (-not $match) { throw "Patient results did not include released request $requestId" }

$interaction = $match.results.drug_interactions | Select-Object -First 1
Write-Host "✅ Patient can see released results." -ForegroundColor Green
Write-Host "   Summary: $($match.results.summary)" -ForegroundColor Gray
if ($interaction) {
  Write-Host "   Interaction: $($interaction.medication1) + $($interaction.medication2) (severity=$($interaction.severity))" -ForegroundColor Gray
  Write-Host "   Recommendation: $($interaction.recommendation)" -ForegroundColor Gray
}
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "✅ Provider-ordered flow test complete" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan


