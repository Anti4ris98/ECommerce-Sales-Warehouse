# Start E-Commerce Data Pipeline
# Unified script to start all services with fresh data (preserves Grafana)

$ErrorActionPreference = "Stop"

Write-Host "`n=== Starting E-Commerce Data Pipeline ===" -ForegroundColor Cyan
Write-Host "Fresh start with preserved Grafana dashboards" -ForegroundColor Yellow

# Step 1: Stop containers and clean volumes (except Grafana)
Write-Host "`n[1/5] Stopping old containers and cleaning data..." -ForegroundColor Yellow
docker-compose down 2>$null

Write-Host "  Removing old data volumes (Grafana preserved)..." -ForegroundColor Gray
docker volume rm ecommerce-sales-warehouse_kafka_data 2>$null
docker volume rm ecommerce-sales-warehouse_zookeeper_data 2>$null
docker volume rm ecommerce-sales-warehouse_postgres_data 2>$null
Write-Host "  ✓ Old data cleaned" -ForegroundColor Green

# Step 2: Start Docker services
Write-Host "`n[2/5] Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Docker containers failed to start!" -ForegroundColor Red
    exit 1
}

# Step 3: Wait for services to be ready
Write-Host "`n[3/5] Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 4: Check container health
Write-Host "`n[4/5] Checking service health..." -ForegroundColor Yellow
docker-compose ps

# Step 5: Apply database schema automatically
Write-Host "`n[5/5] Applying database schema..." -ForegroundColor Yellow
$schemaOutput = powershell -ExecutionPolicy Bypass -File ".\apply_schema.ps1" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Schema applied successfully!" -ForegroundColor Green
}
else {
    Write-Host "✗ Schema application failed!" -ForegroundColor Red
    Write-Host $schemaOutput
}

# Final instructions
Write-Host "`n=== Pipeline Ready! ===" -ForegroundColor Green
Write-Host "`nAll services are running:" -ForegroundColor Cyan
Write-Host "  ✓ PostgreSQL (database)" -ForegroundColor Green
Write-Host "  ✓ Kafka + Zookeeper (streaming)" -ForegroundColor Green
Write-Host "  ✓ Spark (real-time processing)" -ForegroundColor Green
Write-Host "  ✓ Batch ETL (data loading)" -ForegroundColor Green
Write-Host "  ✓ dbt Auto-Refresh (analytics)" -ForegroundColor Green
Write-Host "  ✓ Producer (event generation)" -ForegroundColor Green
Write-Host "  ✓ Grafana (dashboards)" -ForegroundColor Green

Write-Host "`n📊 Access Grafana Dashboard:" -ForegroundColor Cyan
Write-Host "   http://localhost:3000 (admin/admin)" -ForegroundColor White

Write-Host "`n📈 Monitor Pipeline:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f producer" -ForegroundColor Gray
Write-Host "   docker-compose logs -f batch-etl" -ForegroundColor Gray
Write-Host "   docker-compose logs -f dbt-refresh" -ForegroundColor Gray

Write-Host "`n✨ Everything is running automatically - no manual steps needed!" -ForegroundColor Green
Write-Host ""
