# 00 — Master Specification v2 (AI-Driven WhatsApp Sales CRM)

## Infrastructure, Orchestration, and Integration

The integration of generative artificial intelligence into conversational commerce represents a profound paradigm shift. This architecture delineated below is for a self-hosted, open-source WhatsApp AI sales agent in Python, tailored for inbound lead generation via official channels.

## 1. Messaging Infrastructure: Meta Official Cloud API

For a production-grade sales CRM, we utilize the **Official Meta WhatsApp Cloud API**. This provides a RESTful architecture, direct billing, and superior systemic stability compared to unofficial WebSocket-based solutions.

- **Session Management**: Free-form messages within the 24-hour service window opened by inbound user queries.
- **Compliance**: Near-zero risk of algorithmic banning when following Meta commerce policies.
- **Integration**: Python wrappers (e.g., `pygwan` or `whatsapp-api-client-python`) handle OAuth, payloads, and async requests.

## 2. Anthropomorphic Interaction Engineering

Mimicking human behavior through cadence and telemetry to improve trust and conversion.

- **Visual Feedback**: Immediate "Read" receipt (blue checkmarks) + "Typing" indicator (`/Indicators/Typing.json` endpoint).
- **Mathematical Delay**: Artificial latency calculated based on character length (~30ms per character).
- **Natural Spacing**: Large outputs are split into multiple, shorter sequential messages to avoid "walls of text."

## 3. Generative AI Orchestration: LangGraph

A stateful, multi-actor application architecture powered by LangGraph.

- **Cyclical Graph**: The agent loops between reasoning, tool execution, and observation.
- **Stateful Memory**: Persistent, append-only `MessagesState`.
- **Modular Skills**: Every capability is a discrete Python file in a `skills/` directory, bound as a `ToolNode`. This ensures the core loop remains unbroken even as modules are added or removed.

## 4. Implementation of Core Business Modules (Modular Skills)

| Module | Responsibility | Technology |
|--------|----------------|------------|
| **Lead Qualification** | Score intent & extract user data | Zero-shot prompting, JSON extraction |
| **Knowledge Base (RAG)**| Prevent hallucinations, answer FAQs | Vector Embeddings, Cosine Similarity |
| **Payment Gateway** | Generate secure checkout links | Stripe Python SDK, Webhooks |
| **Daily Reporting** | Aggregate metrics & summarize | Cron, PostgreSQL, LLM synthesis |

## 5. Omnichannel CRM Integration: Chatwoot Nexus

Visual dashboard for human operators to monitor, intervene, and control.

- **Centralized Inbox**: Chatwoot logs every event and triggers the AI via webhooks.
- **Human Handoff**: The AI detects edge cases and executes a REST API call to transition control to a human agent in Chatwoot.
- **Data Sync**: Real-time synchronization of conversation history and lead attributes.

## 6. Temporal Orchestration: Auto Follow-Ups

Proactive engagement to re-engage silent prospects while complying with API constraints.

- **Stale Lead Detection**: Hourly cron queries to find silent, high-qualified leads.
- **Template Re-engagement**: Automated dispatch of Meta-approved templates (required for >24h silence).
- **Window Re-opening**: natural dialogue resumes the instant the user replies to a template.

## 7. Security and Scalability

- **Containerization**: Full stack (FastAPI, PostgreSQL, Chatwoot) managed via Docker and EasyPanel.
- **Cryptographic Validation**: Programmatic verification of SHA256 hashes for all Meta Cloud API webhooks.
- **Environment Management**: Secrets injected via `.env` or cloud secret managers; prompt injection detection for user inputs.
