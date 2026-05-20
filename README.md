# Async Shop API

FastAPI project connected to PostgreSQL with asynchronous SQLAlchemy sessions and Alembic migrations.

## Run

```bash
docker compose up --build
```

The API is available at `http://localhost:8001`.

Swagger documentation: `http://localhost:8001/docs`.

PostgreSQL is exposed on `localhost:5433` with:

- database: `zakhar_db`
- user: `user`
- password: `pass`

## Migrations

The application container runs migrations automatically before starting:

```bash
alembic upgrade head
```

The first migration creates users, profiles, categories, products, posts, orders, order_items and reviews, then inserts demo records into each table.

## Screenshots

Database screenshot with all fields and seed data:

- `screenshots/db_tables.png`
- `screenshots/db_tables.html`

## Monitoring

The project includes Prometheus, Grafana, postgres-exporter and cAdvisor in Docker Compose.

```bash
docker compose up -d --build
```

Monitoring URLs:

- FastAPI metrics: `http://localhost:8001/metrics`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (`admin` / `admin`)
- cAdvisor: `http://localhost:8080`

Prometheus scrapes:

- `fastapi-app` - FastAPI `/metrics`
- `postgres` - PostgreSQL metrics from `postgres-exporter`
- `docker-containers` - Docker container metrics from cAdvisor
- `prometheus` - Prometheus self metrics

Grafana is provisioned automatically with:

- Prometheus datasource: `http://prometheus:9090`
- Dashboard: `Shop Monitoring Overview`

Custom metrics:

- `shop_orders_created_total` - total number of created purchases/orders
- `shop_purchases_total_price_total` - cumulative price of all created purchases
- `shop_last_purchase_price` - price of the most recent purchase

Popular dashboards for standard metrics can also be imported in Grafana:

- cAdvisor + Prometheus: dashboard ID `14282`
- Docker monitoring (cAdvisor): dashboard ID `193`
- Docker Dashboard: dashboard ID `11074`
- PostgreSQL Exporter dashboard: dashboard ID `9628` or `14114`

Recommended screenshots for the practical task:

- `screenshots/grafana_shop_monitoring_overview.png`
- `screenshots/prometheus_targets.png`
- `screenshots/fastapi_metrics.png`
- `screenshots/grafana_cadvisor_dashboard.png`
- `screenshots/grafana_postgres_dashboard.png`