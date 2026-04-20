# Wazuh Pulse Monitor

![License](https://img.shields.io/badge/license-MIT-blue)
![Stack](https://img.shields.io/badge/stack-React%20%2B%20FastAPI-22c55e)
![Wazuh](https://img.shields.io/badge/Wazuh-health%20monitor-00a3e0)
![Docker](https://img.shields.io/badge/docker-ready-2496ed)

**Wazuh Pulse Monitor** is an open source operational health dashboard for Wazuh environments.

It focuses on the pulse of the platform: manager state, critical daemons, agent connectivity, cluster health, indexer configuration, API latency, backend errors, SLA-style availability and health notifications.

This is not a SIEM replacement and it does not try to analyze security alerts. Its purpose is simpler and sharper: make it easy to know whether your Wazuh stack is healthy right now.

---

## Highlights

- **Operational Health Score** from `0` to `100`
- **SLA and availability view** for Manager, API, Cluster and Agents
- **Manager daemon status** with running and stopped services
- **Critical daemon weighting** for more realistic health scoring
- **Agent connectivity summary** with active, disconnected, pending and never connected agents
- **Cluster health** with standalone-mode handling
- **Indexer configuration health**
- **API latency tracking** per polling cycle
- **Backend error awareness**
- **Event history** for operational state changes
- **Telegram and Slack health notifications**
- **Docker-ready deployment**
- **No hardcoded credentials**

---

## Screenshots

### Overview

<img width="1603" height="926" alt="Wazuh Pulse Monitor overview dashboard" src="https://github.com/user-attachments/assets/2f68630e-c934-488d-982d-eb1f8b24adc6" />

### Agents

<img width="1590" height="746" alt="Wazuh Pulse Monitor agents table" src="https://github.com/user-attachments/assets/d0a393e8-94bb-49e6-961a-7427f89aa835" />

### Operational History

<img width="1629" height="503" alt="Wazuh Pulse Monitor operational history" src="https://github.com/user-attachments/assets/be1a4e99-1ee5-44d8-96a2-2178f4719d99" />

### Health Details

<img width="1603" height="609" alt="Wazuh Pulse Monitor health details" src="https://github.com/user-attachments/assets/2e638c6e-959b-4e72-be84-6ceba0ed0907" />

### Notifications

<img width="531" height="426" alt="Wazuh Pulse Monitor notifications panel" src="https://github.com/user-attachments/assets/8590ffd6-2e55-4e4e-86ce-a089a5a564d1" />

---

## Health Model

The dashboard calculates a weighted health score using operational signals:

| Signal | Weight |
|---|---:|
| Wazuh API reachable | 15% |
| Manager operational state | 20% |
| Critical daemons running | 20% |
| Connected agents | 15% |
| Indexer available | 10% |
| Cluster healthy | 10% |
| Query latency | 5% |
| Recent backend errors | 5% |

Example:

```text
Health Score: 92/100
Status: green
Critical daemons: 5/5 running
Agents: 2/2 active
API latency: 807 ms average
Backend errors: 0
```

---

## SLA View

The SLA panel presents availability-style metrics:

| Component | Window | Meaning |
|---|---:|---|
| Manager | Last 24h | Observed manager availability |
| API | Last 24h | Wazuh API reachability |
| Cluster | Last 7d | Observed cluster availability |
| Agents | Current | Agent connectivity percentage |

Current note: SLA is based on the in-memory operational history. For production-grade long-term reporting, persist health snapshots in SQLite or PostgreSQL.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS, Recharts |
| Backend | FastAPI, Pydantic, HTTPX |
| Runtime | Python 3.11+, Node.js 20+ |
| Deployment | Docker Compose |
| Integrations | Wazuh API, Telegram, Slack |

---

## Quick Start With Docker

```bash
git clone https://github.com/lHakkul/wazuh-pulse-monitor.git
cd wazuh-pulse-monitor

cp .env.example .env
# Edit .env with your own Wazuh API URL and credentials

docker compose up -d
```

Open:

```text
Dashboard: http://localhost:3000
API docs:  http://localhost:8000/docs
```

---

## Manual Development

### Backend

```bash
cd backend
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

---

## Configuration

Create a `.env` file from `.env.example`.

| Variable | Description | Example |
|---|---|---|
| `WAZUH_API_URL` | Wazuh API base URL | `https://wazuh.example.com:55000` |
| `WAZUH_API_USER` | Wazuh API user | `wazuh` |
| `WAZUH_API_PASSWORD` | Wazuh API password | `change-me` |
| `WAZUH_VERIFY_SSL` | Verify TLS certificates | `false` |
| `ALERT_CHECK_INTERVAL` | Health polling interval in seconds | `60` |
| `HISTORY_MAX_EVENTS` | In-memory event history limit | `200` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | empty by default |
| `TELEGRAM_CHAT_ID` | Telegram chat or channel ID | empty by default |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL | empty by default |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000,http://localhost:5173` |

Never commit your real `.env` file. It is ignored by Git.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Backend liveness check |
| `GET` | `/api/overview` | Global health, score and SLA summary |
| `GET` | `/api/cluster/health` | Cluster health |
| `GET` | `/api/cluster/nodes` | Cluster nodes |
| `GET` | `/api/agents` | Agent list |
| `GET` | `/api/agents/summary` | Agent counts |
| `GET` | `/api/manager/status` | Manager daemon status |
| `GET` | `/api/manager/info` | Manager info |
| `GET` | `/api/history` | Operational event history |
| `DELETE` | `/api/history` | Clear event history |
| `GET` | `/api/alerts/config` | Notification channel status |
| `POST` | `/api/alerts/test/telegram` | Send Telegram test |
| `POST` | `/api/alerts/test/slack` | Send Slack test |

---

## Project Structure

```text
wazuh-pulse-monitor/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── routers/
│   │   └── services/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── services/
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## Security Notes

- This project is designed for defensive monitoring of Wazuh environments you own or are authorized to operate.
- Do not publish real Wazuh credentials, webhook URLs, tokens, IPs or internal hostnames.
- Use least-privilege API credentials where possible.
- Keep the dashboard behind a trusted network, VPN or reverse proxy authentication in production.

---

## Roadmap

- Persistent SLA snapshots with SQLite or PostgreSQL
- Configurable health-score weights
- Dedicated indexer availability checks
- TLS certificate health checks
- Agent stale/old-version detection
- Runbook hints for degraded components
- Authentication for exposed deployments

---

## License

MIT. See [LICENSE](./LICENSE).

---

Wazuh Pulse Monitor is a community project and is not affiliated with Wazuh, Inc.
