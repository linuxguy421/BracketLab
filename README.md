# 🏆 BracketLab

**BracketLab** is a feature-rich, modular tournament management platform designed to handle multiple sports and competition formats with ease.  
It’s built for **local-first operation** with a path toward **cloud deployment** on AWS, leveraging modern technologies like **PyQt6**, **FastAPI**, **Docker**, and **Terraform**.

BracketLab is being developed as both a **desktop application** and an **extensible platform**, supporting everything from casual bar tournaments to large organized leagues.  
Its design emphasizes flexibility, configurability, and future-proofing through modular architecture and clear separation of concerns.

---

## 📜 Project Vision

BracketLab aims to provide a single, unified system that can:
- Manage tournaments for multiple sports (Darts, Shuffleboard, Cornhole, Pool, etc.).
- Handle variable bracket styles and tournament structures.
- Support side pots — special prize pools such as a “Hat Trick Fund” in darts.
- Offer real-time stats, historical tracking, and configurable prize pools.
- Seamlessly transition between a **local GUI** and **cloud-synced mode**.

The ultimate goal is to evolve BracketLab into a **cross-platform, cloud-capable competition management suite**, blending local performance with distributed access and analytics.

---

## 🧩 Core Design Principles

| Principle | Description |
|------------|-------------|
| **Modularity** | BracketLab separates core logic, UI, and cloud APIs into independent modules, making it easy to extend and maintain. |
| **Extensibility** | Each sport can define its own configuration, rules, and prize logic. New sports and formats can be added without rewriting existing systems. |
| **Transparency** | All data (configs, results, players, brackets) is stored in human-readable JSON, ensuring easy debugging and portability. |
| **Persistence** | The system automatically saves configurations, match states, and tournament history. |
| **Cloud Readiness** | While starting as a local PyQt6 app, all core modules are designed to run identically under a FastAPI backend for web or cloud use. |

---

## 🧱 Project Architecture

```
BracketLab/
├── core/
│   ├── config_manager.py
│   ├── tournament_state.py
│   ├── prize_logic.py
│   ├── side_pots.py
│   ├── player_manager.py
│   ├── bracket_parser.py
│   ├── history_manager.py
│   └── logger.py
│
├── ui/            # PyQt6 user interface components (future)
│
├── api/           # FastAPI backend for cloud/web access (future)
│
├── data/          # Persistent data (configs, history, logs)
│
├── tests/         # Unit tests (pytest)
│
├── main.py
└── README.md
```

---

## ⚙️ Installation Guide

### 🐧 Requirements (Arch Linux Example)
```bash
sudo pacman -S python python-pip git
```

### 🧰 Recommended Tools
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Future dependencies:
```
PyQt6
FastAPI
Uvicorn
requests
black
isort
```

### 🚀 Running Locally
```bash
cd BracketLab
python main.py
```

Expected output:
```
BracketLab initialized with config: {}
```

---

## 🧠 Core Modules Overview

### `core/config_manager.py`
Handles reading and writing configuration data (`config.json`).  
Later versions will use **Pydantic models** to enforce schema validation.

### `core/side_pots.py`
Handles secondary prize funds like “Hat Trick” or “High Score” pots.  
Supports per-entry and flat-total contributions configurable per sport.

### `core/logger.py`
Centralized logging using **Loguru** with rotation, retention, and console output.

### `core/player_manager.py`
Stores player and team data (`players.json`), including stats, seeding, and histories.

---

## 💰 Financial System Overview

BracketLab’s financial model will include:
- Entry Fee Management
- Prize Pool Allocation
- Side Pots
- Sponsor Contributions

Example config:
```json
"side_pots": {
  "enabled": true,
  "pots": [
    {"name": "Hat Trick Fund", "per_entry": 1.0},
    {"name": "High Score Bonus", "flat_total": 25.0}
  ]
}
```

---

## 🧪 Testing

BracketLab uses **pytest** for validation.

```bash
pytest
```

---

## ☁️ Cloud Deployment Plan

BracketLab will support **Docker** and **Terraform** deployment with **GitLab CI/CD** automation.

### Planned Stack:
| Component | Purpose |
|------------|----------|
| **AWS ECS / EC2** | Host containerized backend |
| **S3 / EFS** | Persistent storage |
| **GitLab CI/CD** | Build and deploy automation |
| **Terraform** | AWS resource management |
| **Docker Compose** | Local testing |

---

## 🗺️ Development Roadmap

### **Phase 1 – Core Extraction**
- Extract logic from Tkinter script.
- Implement config, logger, and state.
- Add unit tests.

### **Phase 2 – PyQt6 Migration**
- Create main window and tabs.
- Add theming and configuration GUI.

### **Phase 3 – Prize Logic & Side Pots**
- Implement dynamic prize pools and special pots.

### **Phase 4 – Persistence & History**
- Auto-save, archive, and display historical tournaments.

### **Phase 5 – FastAPI Backend**
- REST API and WebSocket support.

### **Phase 6 – Cloud Infrastructure**
- Dockerize, deploy, and automate.

### **Phase 7 – Enhancements & Polish**
- Charts, timers, branding, and league mode.

---

## 🧠 Tech Stack

| Technology | Purpose |
|-------------|----------|
| **Python 3.12+** | Core language |
| **PyQt6** | Desktop GUI |
| **Pydantic** | Config and data validation |
| **FastAPI** | REST API framework |
| **Loguru** | Logging subsystem |
| **Pytest** | Testing framework |
| **Docker** | Containerization |
| **Terraform** | Infrastructure-as-code |
| **GitLab** | Source control + CI/CD |

---

## ✍️ Author

**Greg** – Platform Engineer & Creator of BracketLab  
Building an adaptable, future-ready tournament system that bridges local play and cloud performance.

> “The best way to predict the future of competition management is to build it.”
