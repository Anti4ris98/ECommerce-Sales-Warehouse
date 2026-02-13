# E-Commerce Sales Data Warehouse

Real-time data pipeline simulating e-commerce analytics with Kafka streaming, Spark processing, PostgreSQL warehousing, and Grafana visualization.

---

## Architecture

```
Producer → Kafka → Spark Streaming → Console Output
              ↓
         Batch ETL → PostgreSQL (Star Schema) → dbt Marts → Grafana Dashboards
```

**Data Flow:**
1. **Producer** generates e-commerce events (dynamic users, weighted distribution)
2. **Kafka** streams events to consumers
3. **Spark** processes real-time aggregations
4. **Batch ETL** loads data into PostgreSQL star schema with auto user creation
5. **dbt** creates analytics marts (refreshed every 5 min)
6. **Grafana** visualizes operational & business metrics

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Ingestion** | Python Producer, Kafka, Zookeeper |
| **Processing** | Spark Streaming (PySpark) |
| **Storage** | PostgreSQL (Star Schema) |
| **Analytics** | dbt (data marts) |
| **Visualization** | Grafana |
| **Orchestration** | Docker Compose |

---

## Quick Start

**One command to start everything:**
```powershell
.\start.ps1
```

Then open Grafana: http://localhost:3000 (admin/admin)

**See [SETUP.md](SETUP.md) for detailed instructions.**

---

## Project Structure

```
├── producer.py              # Event generator (dynamic users)
├── batch_etl.py            # Kafka → PostgreSQL ETL
├── spark_streaming.py      # Real-time aggregations
├── start.ps1               # Automated startup
├── stop.ps1                # Stop pipeline
├── apply_schema.ps1        # Database schema setup
├── dbt_refresh.ps1         # Manual dbt refresh
├── docker-compose.yml      # Full stack orchestration
├── Dockerfile.spark        # Spark container
├── requirements.txt        # Python dependencies
├── models/
│   └── schema.sql          # Star schema (4 dims, 1 fact)
├── dbt_project/
│   ├── models/
│   │   ├── staging/        # Staging views
│   │   └── marts/          # customer_ltv, product_performance, daily_sales
│   ├── profiles.yml        # dbt config
│   └── refresh.sh          # dbt auto-refresh script (Docker)
├── dags/
│   └── etl_helpers.py      # Dimension population
├── docs/
│   └── screenshots/        # Dashboard screenshots
├── SETUP.md                # Setup instructions
├── README.md               # Project overview
└── grafana_queries.md      # Dashboard SQL queries
```

---

## Features

✅ **Real-time streaming** (Kafka + Spark)  
✅ **Star schema warehouse** (PostgreSQL)  
✅ **Automated analytics** (dbt auto-refresh every 5 min)  
✅ **Dynamic data generation** (weighted user distribution, auto user creation)  
✅ **One-command deployment** (fully automated startup)  
✅ **Grafana persistence** (dashboards preserved across restarts)  
✅ **Production patterns** (healthchecks, error handling, transaction rollback)

---

## Key Metrics Tracked

**Operational:**
- Total Revenue, Orders, Avg Order Value
- Revenue by Category, Top Products
- Daily Sales Trend, Top Customers

**Business Analytics (dbt):**
- Customer Lifetime Value & Segmentation
- Product Performance Rankings
- Category Comparisons
- Average Customer Metrics

---

## Commands

```powershell
.\start.ps1              # Start entire pipeline (fresh data, preserves Grafana)
.\clean_start.ps1        # Full reset with confirmation
docker-compose logs -f producer     # Monitor event generation
docker-compose logs -f batch-etl    # Monitor ETL
docker-compose logs -f dbt-refresh  # Monitor analytics
```

---

## Portfolio Highlights

- **End-to-end pipeline**: Ingestion → Processing → Storage → Analytics → Visualization
- **Modern stack**: Kafka, Spark, PostgreSQL, dbt, Grafana
- **Production-ready**: Docker orchestration, healthchecks, automated refresh
- **Realistic data**: Dynamic user generation, weighted distributions, auto creation
- **Automated workflow**: Single command deployment, zero manual steps

---

## Documentation

- **[SETUP.md](SETUP.md)** - Complete setup instructions
- **[grafana_queries.md](grafana_queries.md)** - Dashboard SQL queries
- **[docs/screenshots](docs/screenshots)** - Dashboard screenshots
