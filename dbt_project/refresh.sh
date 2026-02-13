#!/bin/bash
# dbt refresh script for Docker container

echo "🔄 dbt Auto-Refresh Service Started"
echo "Refresh interval: ${DBT_REFRESH_INTERVAL:-300} seconds"
echo "Waiting 60 seconds for database to be ready..."
sleep 60

iteration=0

while true; do
    iteration=$((iteration + 1))
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] Iteration #$iteration - Running dbt models..."
    
    cd /dbt_project
    dbt run --profiles-dir . 2>&1 | grep -E "(PASS=|ERROR=|Done\.|Completed)"
    
    if [ $? -eq 0 ]; then
        echo "  ✅ dbt models refreshed successfully"
    else
        echo "  ❌ dbt run failed (will retry)"
    fi
    
    echo "  ⏳ Waiting ${DBT_REFRESH_INTERVAL:-300} seconds until next refresh..."
    sleep ${DBT_REFRESH_INTERVAL:-300}
done
