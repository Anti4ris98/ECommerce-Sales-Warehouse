# Setup Guide

Complete setup in 3 steps.

---

## Prerequisites

- Docker Desktop
- Python 3.12
- PowerShell (Windows) or Bash (Linux/Mac)

---

## Step 1: Clone & Install Dependencies

```powershell
git clone https://github.com/your-username/ECommerce-Sales-Warehouse.git
cd ECommerce-Sales-Warehouse

# Create virtual environment (optional, for manual dbt runs)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Start Everything

**Single command:**
```powershell
.\start.ps1
```

**What it does:**
1. Cleans old data (preserves Grafana dashboards)
2. Starts 7 Docker services (Postgres, Kafka, Zookeeper, Spark, batch-etl, dbt-refresh, producer)
3. Applies database schema
4. Populates dimensions (products, users, dates, categories)

**Wait 30 seconds for initialization.**

---

## Step 3: Access Grafana

**URL:** http://localhost:3000  
**Login:** admin / admin

**Configure Data Source:**
1. Connections → Data sources → Add PostgreSQL
2. Settings:
   - Host: `postgres:5432`
   - Database: `ecommerce_dw`
   - User: `user`
   - Password: `password`
   - TLS/SSL: disable
3. Save & Test

**Create Dashboards:**  
If dashboards are not available you coul reecreate them by using this queries [grafana_queries.md](grafana_queries.md)

---

## Monitoring

```powershell
# Check services
docker-compose ps

# View logs
docker-compose logs -f producer
docker-compose logs -f batch-etl
docker-compose logs -f dbt-refresh

# Verify data
docker exec -it ecommerce-sales-warehouse-postgres-1 psql -U user -d ecommerce_dw -c "SELECT COUNT(*) FROM fact_sales;"
```

---

## Commands

```powershell
.\start.ps1          # Start pipeline
.\stop.ps1           # Stop pipeline
```

---

## Services

All services start automatically with `start.ps1`:

| Service | Purpose |
|---------|---------|
| **postgres** | Data warehouse (PostgreSQL) |
| **kafka** | Event streaming |
| **zookeeper** | Kafka coordination |
| **spark-job** | Real-time processing |
| **batch-etl** | Kafka → Postgres ETL |
| **dbt-refresh** | Analytics refresh (every 5 min) |
| **producer** | Event generation |
| **grafana** | Dashboards |

**dbt-refresh - could take a while to initialize (around 2-3 minutes)**
**No manual steps needed** - everything runs automatically!

---

**Full project info:** [README.md](README.md)  
**Dashboard queries:** [grafana_queries.md](grafana_queries.md)
