# Stop all containers and clean up

Write-Host "Stopping all containers..." -ForegroundColor Yellow
docker-compose down

Write-Host "`nContainers stopped successfully!" -ForegroundColor Green
Write-Host "`nTo remove volumes (delete all data):" -ForegroundColor Yellow
Write-Host "  docker-compose down -v" -ForegroundColor White
