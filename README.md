# Botzo.io — Lightweight Open-Source AI Agent & Webhook Orchestrator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**Botzo.io** is an open-source, zero-bloat framework for building, routing, and orchestrating autonomous AI agents and asynchronous webhook workflows. Designed for developers and digital agencies, it bridges the gap between LLM tool-calling pipelines and real-world API triggers without heavy infrastructure overhead.

---

## Key Features

* **Deterministic Tool Routing:** Register standard Python functions as structured tools that LLM agents can inspect and invoke safely.
* **Webhook-First Architecture:** Built-in event listeners normalize payloads from GitHub, Slack, Discord, and custom REST endpoints.
* **Automatic Retry & Backoff:** Resilient execution engine handles rate limits and transient API failures out of the box.
* **Provider Agnostic:** Seamlessly plug in Anthropic Claude, OpenAI, or local open-weights models via a unified interface.

---

## Quick Start

### 1. Installation

Clone the repository and install the core module:

```bash
git clone https://github.com/talentwaveagencyltd-bot/botzo.io.git
cd botzo.io
```

### 2. Define Your First Agent Workflow

```python
from botzo import BotzoAgent, Tool

# 1. Initialize the orchestrator
agent = BotzoAgent(name="support-triage", model="claude-3-7-sonnet-latest")

# 2. Register a custom tool
@agent.register_tool(description="Fetch live status of a deployment service")
def check_service_health(service_name: str) -> dict:
    return {"service": service_name, "status": "healthy", "latency_ms": 42}

# 3. Execute a task
response = agent.run("Check the health of the auth-api service and summarize.")
print(response)
```

---

## Architecture Overview

```text
Incoming Webhook / Trigger
         │
         ▼
┌─────────────────────┐
│   Botzo Event Bus   │ ──► Validates & normalizes payload
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Agent Orchestrator │ ──► Evaluates context & selects registered tools
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Tool Sandbox      │ ──► Executes Python functions & returns structured JSON
└─────────────────────┘
```

---

## Contributing

We welcome contributions from the open-source community!
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
