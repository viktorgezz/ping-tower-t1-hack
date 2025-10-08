# Ansible + Docker Compose Infra Project
**Purpose:** An Ansible playbook that installs Docker, Docker Compose (plugin), Git and deploys a Docker Compose stack
containing: PostgreSQL, ClickHouse, Elasticsearch (7.x), Grafana, Prometheus, Redis, Nginx (reverse proxy) and a placeholder
Celery service. Use this as a starting point and replace placeholder images / secrets with your production images/values.

## Structure
```
infra_ansible_project/
├── ansible.cfg
├── inventory.ini
├── site.yml
├── docker-compose.yml
├── .env.example
├── prometheus/
│   └── prometheus.yml
├── grafana/
│   └── provisioning/
│       └── dashboards/
│           └── example-dashboard.json
└── nginx/
    └── default.conf
```

## Quick steps (one-liner)
1. Ensure you can SSH to the target server from your control machine and update `inventory.ini` with its address.
2. Run:
```bash
ansible-playbook -i inventory.ini site.yml
```
The playbook will:
- install prerequisites (apt packages)
- install Docker (official repo)
- install Docker Compose plugin
- enable and start docker
- copy docker-compose.yml and supporting configs to `/opt/infra`
- run `docker compose up -d` in `/opt/infra`

## Customize
- Edit `.env.example` → `/opt/infra/.env` on the host (or change via Ansible vars) to set passwords and ports.
- Replace the placeholder `celery` service image in `docker-compose.yml` with your app image that runs `celery -A <app> worker`.
- For Elasticsearch production usage, review memory and security settings; adjust `elasticsearch` settings before deployment.

## Files of interest
- `site.yml` — the Ansible playbook you run.
- `docker-compose.yml` — stack definition.
- `prometheus/prometheus.yml` — Prometheus scrape config (basic).
- `nginx/default.conf` — sample reverse proxy config for services.

## Notes & warnings
- Elasticsearch may require specific kernel and vm.max_map_count settings. The playbook sets a recommended value (`vm.max_map_count=262144`).
- This project is intended as a local/dev bootstrap. For production, add backups, volume management, TLS, secrets manager, monitoring auth, and resource constraints.
