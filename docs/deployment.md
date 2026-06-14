# AgentLoop Deployment Guide

## Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- 8GB RAM minimum (16GB recommended)
- 20GB disk space

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sam1064max/agentloop.git
cd agentloop
```

### 2. Create Environment File

Create `.env` in the project root:

```bash
# Database
DATABASE_URL=postgresql://agentloop:agentloop@db:5432/agentloop

# Analytics
DUCKDB_PATH=/data/analytics.db

# Security
API_SECRET_KEY=your-secret-key-here

# Optional: External Services
# REDIS_URL=redis://cache:6379
```

### 3. Build and Start

```bash
# Build images and start all services
docker compose up -d --build

# Verify all services are running
docker compose ps
```

### 4. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Access Grafana
open http://localhost:3000  # admin/admin
```

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 8080 | Dashboard UI |
| API | 8000 | REST API |
| Analytics | 8001 | Analytics service |
| PostgreSQL | 5432 | Database |
| Prometheus | 9090 | Metrics |
| Grafana | 3000 | Dashboards |

## Configuration

### API Service

Environment variables for `./backend/Dockerfile`:

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | - | PostgreSQL connection string |
| API_SECRET_KEY | - | JWT signing key |
| LOG_LEVEL | INFO | Logging level |
| CORS_ORIGINS | * | Allowed CORS origins |
| RATE_LIMIT_REQUESTS | 100 | Requests per minute |

### Analytics Service

Environment variables for `./analytics/Dockerfile`:

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | - | PostgreSQL connection string |
| DUCKDB_PATH | /data/analytics.db | DuckDB file path |
| ETL_SCHEDULE | 0 * * * * | Cron schedule for ETL |
| INSIGHTS_ENABLED | true | Enable insights generation |

### Database

PostgreSQL 16 with the following configuration:

- **Username**: agentloop
- **Password**: agentloop
- **Database**: agentloop

To connect externally:
```bash
psql -h localhost -p 5432 -U agentloop -d agentloop
```

## Production Deployment

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml agentloop
```

### Kubernetes

Helm chart available at `infrastructure/helm/`:

```bash
helm install agentloop ./infrastructure/helm/agentloop \
  --set database.url=$DATABASE_URL \
  --set api.secretKey=$API_SECRET_KEY
```

### Cloud Providers

#### AWS ECS

```bash
# Push images to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
docker tag agentloop-api:latest $ECR_REGISTRY/agentloop-api:latest
docker push $ECR_REGISTRY/agentloop-api:latest

# Update task definition and run
aws ecs update-service --cluster agentloop --service api --force-new-deployment
```

#### GCP Cloud Run

```bash
# Build and push to Artifact Registry
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT/agentloop/api

# Deploy
gcloud run deploy agentloop-api \
  --image $REGION-docker.pkg.dev/$PROJECT/agentloop/api \
  --set-envvars DATABASE_URL=$DATABASE_URL
```

## Monitoring Setup

### Prometheus Targets

After startup, Prometheus automatically scrapes:
- `api:8000` - API metrics
- `analytics:8001` - Analytics service metrics

Verify targets: http://localhost:9090/targets

### Grafana Dashboards

1. Login to Grafana (http://localhost:3000)
2. Navigate to Dashboards → Import
3. Import dashboard JSON from `infrastructure/grafana/dashboards/`

### Alerting

Create alerts in Grafana:

1. Alerting → Alert rules → Create rule
2. Select Prometheus data source
3. Define conditions (e.g., error_rate > 5%)
4. Set notification channel

## Database Migrations

Run migrations on startup or manually:

```bash
# Run pending migrations
docker compose exec api alembic upgrade head

# Create new migration
docker compose exec api alembic revision --autogenerate -m "Add new table"

# Check migration status
docker compose exec api alembic current
```

## Backup & Recovery

### Backup PostgreSQL

```bash
# Create backup
docker compose exec db pg_dump -U agentloop agentloop > backup_$(date +%Y%m%d).sql

# Restore from backup
cat backup_20260315.sql | docker compose exec -T db psql -U agentloop agentloop
```

### Backup DuckDB

```bash
# Stop analytics service
docker compose stop analytics

# Copy database file
docker compose cp analytics:/data/analytics.db ./backups/

# Restart service
docker compose start analytics
```

## Scaling

### Horizontal Scaling

```bash
# Scale API service
docker compose up -d --scale api=3

# Scale analytics service
docker compose up -d --scale analytics=2
```

### Database Scaling

For production, use managed database services:
- AWS RDS PostgreSQL
- Google Cloud SQL
- Azure Database for PostgreSQL

## Health Checks

### API Health

```bash
curl http://localhost:8000/health
# {"status": "healthy", "version": "1.0.0", "db": "connected"}
```

### Database Connection

```bash
docker compose exec api python -c "from app.db import SessionLocal; SessionLocal().execute('SELECT 1')"
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs api

# Common issues:
# - Port already in use: Change port mapping
# - Database connection: Verify DATABASE_URL
```

### Database Connection Issues

```bash
# Test database connectivity
docker compose exec db pg_isready -U agentloop

# Check connection string format
# postgresql://user:password@host:port/database
```

### High Memory Usage

```bash
# Check container resource usage
docker stats

# Reduce memory limits in docker-compose.yml if needed
```

## Security Checklist

- [ ] Change default database passwords
- [ ] Use TLS in production (reverse proxy)
- [ ] Set `API_SECRET_KEY` to random 256-bit value
- [ ] Restrict CORS_ORIGINS to your domains
- [ ] Enable PostgreSQL SSL for connections
- [ ] Regular security updates: `docker compose pull`