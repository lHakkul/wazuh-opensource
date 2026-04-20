"""Datos de demostración cuando WAZUH_MOCK=true."""
import random
from datetime import datetime, timedelta


def _rand_keepalive(minutes_ago_max=120):
    delta = timedelta(minutes=random.randint(0, minutes_ago_max))
    return (datetime.utcnow() - delta).isoformat() + "Z"


MOCK_OVERVIEW = {
    "timestamp": None,
    "global_status": "yellow",
    "cluster": {
        "status": "green",
        "enabled": True,
        "running": True,
        "nodes": [
            {"name": "master-node", "type": "master", "version": "4.7.0", "address": "10.0.0.1", "status": "connected"},
            {"name": "worker-01",   "type": "worker", "version": "4.7.0", "address": "10.0.0.2", "status": "connected"},
            {"name": "worker-02",   "type": "worker", "version": "4.7.0", "address": "10.0.0.3", "status": "disconnected"},
        ],
    },
    "manager": {
        "status": "yellow",
        "enabled": ["wazuh", "wazuh_db", "wazuh_analysisd", "wazuh_remoted", "wazuh_logcollector",
                    "wazuh_integratord", "wazuh_monitord", "wazuh_syscheckd", "wazuh_execd",
                    "wazuh_authd", "wazuh_clusterd", "wazuh_apid", "wazuh_modulesd"],
        "running": ["wazuh", "wazuh_db", "wazuh_analysisd", "wazuh_remoted", "wazuh_logcollector",
                    "wazuh_execd", "wazuh_authd", "wazuh_clusterd", "wazuh_apid", "wazuh_modulesd"],
        "stopped": ["wazuh_integratord", "wazuh_syscheckd", "wazuh_monitord"],
    },
    "agents": {
        "total": 24,
        "active": 18,
        "disconnected": 4,
        "pending": 1,
        "never_connected": 1,
        "agents": [],
    },
    "components": [
        {"name": "cluster", "status": "green"},
        {"name": "manager", "status": "yellow"},
        {"name": "agents",  "status": "yellow"},
    ],
}

_AGENT_NAMES = [
    ("srv-web-01", "10.0.1.10", "active", "Ubuntu 22.04", "linux"),
    ("srv-web-02", "10.0.1.11", "active", "Ubuntu 22.04", "linux"),
    ("srv-db-01",  "10.0.2.10", "active", "CentOS 8", "linux"),
    ("srv-db-02",  "10.0.2.11", "disconnected", "CentOS 8", "linux"),
    ("win-pc-01",  "192.168.1.20", "active", "Windows 11", "windows"),
    ("win-pc-02",  "192.168.1.21", "active", "Windows 10", "windows"),
    ("win-pc-03",  "192.168.1.22", "disconnected", "Windows 10", "windows"),
    ("macos-dev",  "192.168.1.50", "active", "macOS 14", "darwin"),
    ("kube-node-01", "10.0.3.10", "active", "Ubuntu 20.04", "linux"),
    ("kube-node-02", "10.0.3.11", "active", "Ubuntu 20.04", "linux"),
    ("firewall-01",  "10.0.0.254", "active", "pfSense", "linux"),
    ("proxy-01",     "10.0.1.1",  "active", "Debian 12", "linux"),
    ("elk-node-01",  "10.0.4.10", "active", "Ubuntu 22.04", "linux"),
    ("elk-node-02",  "10.0.4.11", "disconnected", "Ubuntu 22.04", "linux"),
    ("jenkins-01",   "10.0.5.10", "active", "Ubuntu 22.04", "linux"),
    ("monitoring",   "10.0.5.20", "active", "Debian 12", "linux"),
    ("backup-srv",   "10.0.6.10", "active", "Rocky Linux 9", "linux"),
    ("mail-srv",     "10.0.7.10", "active", "Ubuntu 20.04", "linux"),
    ("vpn-gw",       "10.0.0.10", "active", "OpenBSD 7", "linux"),
    ("win-srv-01",   "192.168.2.10", "active", "Windows Server 2022", "windows"),
    ("win-srv-02",   "192.168.2.11", "active", "Windows Server 2019", "windows"),
    ("iot-gateway",  "10.0.8.10", "pending", "Raspbian 11", "linux"),
    ("legacy-srv",   "10.0.9.10", "disconnected", "CentOS 7", "linux"),
    ("test-vm",      None,        "never_connected", None, None),
]


def get_mock_agents():
    agents = []
    for i, (name, ip, status, os_name, os_platform) in enumerate(_AGENT_NAMES, start=1):
        agents.append({
            "id": str(i),
            "name": name,
            "ip": ip,
            "status": status,
            "version": "4.7.0" if status != "never_connected" else None,
            "os_name": os_name,
            "os_platform": os_platform,
            "last_keepalive": _rand_keepalive() if status == "active" else _rand_keepalive(1440),
            "manager": "master-node",
            "group": ["default"],
        })
    return agents


def get_mock_overview():
    from datetime import datetime
    data = dict(MOCK_OVERVIEW)
    data["timestamp"] = datetime.utcnow().isoformat()
    data["agents"] = dict(data["agents"])
    data["agents"]["agents"] = get_mock_agents()
    return data


MOCK_HISTORY = [
    {"event_type": "status_change", "severity": "yellow", "component": "manager",
     "message": "wazuh_syscheckd detenido — revisar configuración", "minutes_ago": 5},
    {"event_type": "agents_disconnected", "severity": "yellow", "component": "agents",
     "message": "4 agentes desconectados detectados", "minutes_ago": 12},
    {"event_type": "status_change", "severity": "red", "component": "cluster",
     "message": "worker-02 perdió conexión con el clúster", "minutes_ago": 35},
    {"event_type": "status_change", "severity": "green", "component": "cluster",
     "message": "worker-02 reconectado al clúster", "minutes_ago": 28},
    {"event_type": "status_change", "severity": "green", "component": "manager",
     "message": "Todos los daemons críticos operativos", "minutes_ago": 60},
]
