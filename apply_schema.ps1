# Apply PostgreSQL schema to database

Write-Host "=== Applying PostgreSQL Schema ===" -ForegroundColor Cyan

# Check if Postgres container is running
$postgresStatus = docker ps --filter "name=ecommerce-sales-warehouse-postgres-1" --format "{{.Status}}"
if (-not $postgresStatus) {
    Write-Host "[ERROR] Postgres container is not running!" -ForegroundColor Red
    Write-Host "Start services with: .\start.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Postgres container is running: $postgresStatus" -ForegroundColor Green
Write-Host ""

Write-Host "Applying schema from models/schema.sql..." -ForegroundColor Yellow

# Apply schema using PowerShell pipe (not bash redirect)
Get-Content models\schema.sql | docker exec -i ecommerce-sales-warehouse-postgres-1 psql -U user -d ecommerce_dw

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    
Write-Host "`n[SUCCESS] Schema applied successfully!" -ForegroundColor Green

Write-Host "`nPopulating dimension tables..." -ForegroundColor Yellow
python dags\etl_helpers.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] All dimension tables populated!" -ForegroundColor Green
    Write-Host "`nDatabase is ready! Start the producer:" -ForegroundColor Cyan
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "   python producer.py" -ForegroundColor White
} else {
    Write-Host "`n[ERROR] Failed to populate dimensions!" -ForegroundColor Red
    Write-Host "Try running manually: python dags\etl_helpers.py" -ForegroundColor Yellow
}
}
else {
    Write-Host ""
    Write-Host "[ERROR] Failed to apply schema!" -ForegroundColor Red
    exit 1
}
