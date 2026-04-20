# Wazuh Pulse Monitor

Dashboard SOC para monitorear en tiempo real el estado de salud del ecosistema Wazuh: managers, indexers, agentes conectados/desconectados, estado del clúster, historial de eventos y alertas por Telegram y Slack.

![License](https://img.shields.io/badge/license-MIT-blue)
![Stack](https://img.shields.io/badge/stack-React%20%2B%20FastAPI-informational)
![Docker](https://img.shields.io/badge/docker-ready-success)

---

## Características

- **Vista general del ecosistema Wazuh** — estado global del clúster, manager y agentes
- **Monitoreo del clúster** — lista de nodos con estado online/offline
- **Estado del Manager** — daemons activos y detenidos en tiempo real
- **Tabla de agentes** — búsqueda, filtros y ordenamiento; estado activo/desconectado
- **Historial de eventos** — registro de cambios de estado en memoria
- **Alertas automáticas** — Telegram y Slack cuando un componente cae o se recupera
- **Actualización automática** — refresco cada 30 segundos sin recarga de página
- **Configuración por `.env`** — sin credenciales hardcodeadas
- **Docker-ready** — despliegue con `docker compose up`

---

## Requisitos

- Docker y Docker Compose (recomendado)
- O bien: Python 3.11+ y Node.js 20+
- Acceso a la API REST de Wazuh (puerto 55000)

---

## Inicio rápido con Docker

```bash
# 1. Clona el repositorio
git clone https://github.com/TU_USUARIO/wazuh-pulse-monitor.git
cd wazuh-pulse-monitor

# 2. Copia y edita la configuración
cp .env.example .env
nano .env  # Ajusta WAZUH_API_URL, usuario y contraseña

# 3. Levanta los servicios
docker compose up -d

# 4. Abre el dashboard
# → http://localhost:3000
```

---

## Inicio manual (desarrollo)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env          # Edita el .env
uvicorn app.main:app --reload --port 8000
```

Documentación interactiva de la API disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## Configuración (.env)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `WAZUH_API_URL` | URL base de la API de Wazuh | `https://192.168.1.10:55000` |
| `WAZUH_API_USER` | Usuario de la API | `wazuh` |
| `WAZUH_API_PASSWORD` | Contraseña de la API | `MiPassword123` |
| `WAZUH_VERIFY_SSL` | Verificar certificado SSL | `false` |
| `ALERT_CHECK_INTERVAL` | Segundos entre verificaciones | `60` |
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram | `123456:ABC...` |
| `TELEGRAM_CHAT_ID` | ID del chat o canal | `-100123456789` |
| `SLACK_WEBHOOK_URL` | URL Incoming Webhook de Slack | `https://hooks.slack.com/...` |

### Configurar alertas Telegram

1. Habla con [@BotFather](https://t.me/BotFather) y crea un bot → obtendrás el token
2. Añade el bot a un grupo o canal y obten el chat ID con `@userinfobot`
3. Pon los valores en el `.env` y reinicia el backend
4. Ve a la pestaña **Alertas** en el dashboard → botón "Probar"

### Configurar alertas Slack

1. En tu workspace de Slack: **Apps → Incoming Webhooks → Add New Webhook**
2. Elige el canal y copia la URL del webhook
3. Pega la URL en `SLACK_WEBHOOK_URL` en el `.env`

---

## Estructura del proyecto

```
wazuh-pulse-monitor/
├── backend/
│   ├── app/
│   │   ├── main.py             # Entrada FastAPI + lifespan
│   │   ├── config.py           # Settings via pydantic-settings
│   │   ├── models/schemas.py   # Modelos Pydantic
│   │   ├── services/
│   │   │   ├── wazuh.py        # Cliente HTTP para la API de Wazuh
│   │   │   ├── alerts.py       # Telegram + Slack
│   │   │   └── history.py      # Buffer circular de eventos
│   │   └── routers/
│   │       ├── overview.py     # GET /api/overview
│   │       ├── cluster.py      # GET /api/cluster/health
│   │       ├── agents.py       # GET /api/agents
│   │       ├── manager.py      # GET /api/manager/status
│   │       ├── history.py      # GET /api/history
│   │       └── alerts.py       # POST /api/alerts/test/*
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Tabs: Overview / Agentes / Historial / Alertas
│   │   ├── components/         # UI modular
│   │   ├── hooks/useWazuh.js   # Polling automático
│   │   └── services/api.js     # Llamadas al backend
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/overview` | Estado global del ecosistema |
| `GET` | `/api/cluster/health` | Salud del clúster |
| `GET` | `/api/cluster/nodes` | Lista de nodos |
| `GET` | `/api/agents` | Lista completa de agentes |
| `GET` | `/api/agents/summary` | Resumen numérico |
| `GET` | `/api/manager/status` | Estado de daemons |
| `GET` | `/api/history` | Historial de eventos |
| `DELETE` | `/api/history` | Limpiar historial |
| `GET` | `/api/alerts/config` | Canales configurados |
| `POST` | `/api/alerts/test/telegram` | Enviar mensaje de prueba |
| `POST` | `/api/alerts/test/slack` | Enviar mensaje de prueba |

---

## Publicar en GitHub

```bash
# Inicializar el repositorio
git init
git add .
git commit -m "feat: initial release — Wazuh Pulse Monitor v1.0"

# Crear el repo en GitHub (requiere gh CLI)
gh repo create wazuh-pulse-monitor --public --description "Dashboard SOC para monitorear el ecosistema Wazuh"

# Subir el código
git branch -M main
git remote add origin https://github.com/TU_USUARIO/wazuh-pulse-monitor.git
git push -u origin main
```

---

## Contribuir

1. Haz fork del repositorio
2. Crea una rama: `git checkout -b feature/mi-mejora`
3. Haz tus cambios y commitea: `git commit -m 'feat: mi mejora'`
4. Abre un Pull Request

---

## Licencia

MIT — ver [LICENSE](./LICENSE)

---

> **Aviso:** Este proyecto no está afiliado oficialmente con Wazuh, Inc. Es una herramienta de comunidad open source.
