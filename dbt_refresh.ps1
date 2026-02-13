# Auto-refresh dbt models periodically
# Run this in background to keep analytics tables up-to-date

param(
    [int]$IntervalMinutes = 5  # Refresh every 5 minutes
)

Write-Host "=== dbt Auto-Refresh ===" -ForegroundColor Cyan
Write-Host "Refreshing dbt models every $IntervalMinutes minutes..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Gray

$iteration = 0

while ($true) {
    $iteration++
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    Write-Host "[$timestamp] Iteration #$iteration - Running dbt..." -ForegroundColor Green
    
    Push-Location dbt_project
    
    # Run dbt models
    $output = dbt run --profiles-dir . 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        # Parse output for success count
        $successLine = $output | Select-String "Done\. PASS="
        Write-Host "  ✅ $successLine" -ForegroundColor Green
    } else {
        Write-Host "  ❌ dbt run failed!" -ForegroundColor Red
        Write-Host $output -ForegroundColor Red
    }
    
    Pop-Location
    
    Write-Host "  ⏳ Waiting $IntervalMinutes minutes until next refresh...`n" -ForegroundColor Gray
    Start-Sleep -Seconds ($IntervalMinutes * 60)
}
