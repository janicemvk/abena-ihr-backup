# Abena IHR – Setup & Run Guide

This repository contains the complete Abena Intelligent Health Records platform: API gateway, clinical services, telemedicine apps, dashboards, biomarker tooling, ingestion layers, and reference datasets. Follow the steps below after pulling the repo to bring the stack up locally.

--- 

## 1. Prerequisites

- 4+ CPU cores, 16 GB RAM, 40 GB free disk
- Docker 24+ and Docker Compose Plugin 2.20+
- Node.js 18+ (for local service development)
- Python 3.11+ (for service scripts/tests)
- `git`, `curl`, `psql`, `sudo`

> **Tip:** When you edit code that runs inside Docker, rebuild the specific service (`docker compose build <service>`) so cached containers pick up your changes.

---

## 2. Clone and prepare

```bash
git clone https://github.com/<your-org>/abena.git
cd /var/www/html/abena

# Make helper scripts executable once
chmod +x start-abena-system.sh test-system.sh setup-live-database.sh \
        import-live-database.sh export-local-database.sh rebuild-service.sh
```

Place the provided SQL dumps (e.g., `ABENA PATIENT DATABASE.sql`) in the repo root if they are not already identical to what you pulled.

---

## 3. Configure environment

`start-abena-system.sh` auto-generates a baseline `.env` if missing. Review/update it before running in non-dev environments:

```bash
nano .env   # adjust POSTGRES_*, JWT_SECRET, API_KEY, etc.
```

For custom Docker ports/credentials, keep the values in sync with `docker-compose.simple.yml`.

---

## 4. Launch the full stack (recommended)

```bash
./start-abena-system.sh
```

What this script does:
- Verifies Docker is up and all critical files exist.
- Creates `.env` (first run only).
- Optionally clears old volumes.
- Builds every image and starts the compose stack defined in `docker-compose.simple.yml`.
- Performs health checks for: Postgres, module registry, background modules, Abena IHR core, business rules, telemedicine, API gateway.

When the script completes, inspect services:

```bash
docker ps
curl http://localhost:8080/health          # API gateway (mapped from container port 80)
curl http://localhost:3003/modules         # Module registry
curl http://localhost:4001/health          # Background modules
```

To tail logs:

```bash
docker compose -f docker-compose.simple.yml logs -f
```

---

## 5. Manual compose workflow (advanced)

```bash
docker compose -f docker-compose.simple.yml up --build -d
# or rebuild a single service after code changes
docker compose -f docker-compose.simple.yml build provider-dashboard
docker compose -f docker-compose.simple.yml up provider-dashboard
```

> For Node-based services, prefer `sudo npm install` inside the project folder before rebuilding so dependencies match the user’s environment expectations.

Stop/reset:

```bash
docker compose -f docker-compose.simple.yml down            # stop
docker compose -f docker-compose.simple.yml down -v         # stop + clear volumes
```

---

## 6. Database bootstrap options

1. **Automatic via start script** – loads bundled SQL dumps into the Postgres service.
2. **Manual live setup** – customize and run:
   ```bash
   ./setup-live-database.sh
   ```
3. **Import/Export helpers**
   ```bash
   ./import-live-database.sh
   ./export-local-database.sh
   ```

Postgres is published on host port `5433` (container 5432). Connect with:

```bash
psql -h localhost -p 5433 -U abena_user -d abena_ihr
```

---

## 7. Test the deployment

```bash
./test-system.sh

# Targeted checks
curl http://localhost:8080/health
curl http://localhost:3003/modules
curl http://localhost:4002/health
```

You can also run the Python smoke tests located at the repo root:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r abena_comprehensive_test_suite/requirements.txt
pytest test_frontend_endpoint.py test_appointment_flow.py
```

---

## 8. Local service development

Run individual modules outside Docker when iterating:

```bash
# Database only
docker compose -f docker-compose.simple.yml up postgres -d

# Background modules (Node)
cd "12 Core Background Modules"
sudo npm install
sudo npm run dev

# Abena IHR FastAPI service
cd abena_ihr
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 4002
```

Point local services at the running Postgres instance (`DATABASE_URL=postgresql://abena_user:abena_password@localhost:5433/abena_ihr`).

---

## 9. Key service endpoints

- API Gateway: `http://localhost:8080` (proxy to all modules)
- Module Registry: `http://localhost:3003`
- Background Modules: `http://localhost:4001`
- Abena IHR Core API: `http://localhost:4002`
- Business Rule Engine: `http://localhost:4003`
- Telemedicine Web App: `http://localhost:4004`
- Provider Dashboard: `http://localhost:4008`
- Patient Dashboard: `http://localhost:4009`
- Biomarker GUI (Dash): `http://localhost:4012`

Use `/health` on each service to confirm uptime.

---

## 10. Troubleshooting quick wins

- **Ports already used**: `sudo lsof -i :8080` (replace port) and stop conflicting processes.
- **Services not updating after code edits**: rebuild the affected image (`docker compose build <service>`). Remember Docker caches files until rebuilt.
- **Postgres refuses connections**: verify container is up (`docker ps`), then `docker logs abena-postgres`.
- **Module failing health check**: `docker compose logs <service>`; most services expose `/health` for detailed diagnostics.
- **Need a clean slate**: `docker compose -f docker-compose.simple.yml down -v && docker system prune -f`.

---

## 11. Next steps for production

1. Swap sample secrets in `.env` for secure values.
2. Add TLS certificates to `api_gateway/nginx.conf`.
3. Configure automated backups via `export-local-database.sh` or managed tooling.
4. Hook your monitoring stack (Prometheus/Grafana) to container metrics.
5. Review `DEPLOYMENT_GUIDE.md`, `LIVE_DEPLOYMENT_CHECKLIST.md`, and `SYSTEM_STATUS.md` for operational policies.

You now have everything needed to pull this repo, stand up the complete Abena ecosystem locally, and begin iterating confidently. 🚀

