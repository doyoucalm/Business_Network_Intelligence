# Business Network Intelligence (BNI) Hub
> **Empowering BNI Chapters with Fluid Data & AI-Driven Insights.**

Business Network Intelligence is a specialized digital infrastructure designed for BNI (Business Network International) chapters. It replaces fragmented Google Forms and Excel sheets with a centralized, AI-powered command center for managing education, growth, and member engagement.

## 🚀 Key Features

- **Fluid Database Architecture**: Powered by PostgreSQL with JSONB support, allowing the system to adapt to new data types (Roster, PALMS, Visitor logs) without rigid schema migrations.
- **Context-Aware AI Assistant**: Integrated with DeepSeek (via OpenRouter) to provide real-time assistance based on the specific page or data the user is viewing.
- **Role-Based Access (RBAC)**: Secure authentication and routing tailored for different chapter roles (Growth Coordinator, Education Coordinator, etc.).
- **Automated Infrastructure**: Deployment-ready with Docker and Caddy, featuring automatic SSL/TLS via Let's Encrypt.
- **Edu-Moment Hub**: A centralized repository for chapter education materials with search and filter capabilities.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.12+)
- **Frontend**: Modern Vanilla JS & CSS (Fast, lightweight, and dependency-free)
- **Database**: PostgreSQL (Hybrid Relational/Document)
- **Reverse Proxy**: Caddy (Auto-HTTPS)
- **Containerization**: Docker & Docker Compose
- **AI Engine**: OpenRouter (DeepSeek-V3)

## 📦 Getting Started

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for local development)

### 2. Setup Environment
Clone the repository and create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your credentials and OpenRouter API Key
```

### 3. Launch with Docker
```bash
docker-compose up -d
```
The application will be available at `http://localhost:8000` (or your configured domain with HTTPS).

## 📂 Project Structure

- `app/`: FastAPI backend logic, models, and AI integration.
- `static/`: Frontend assets (CSS, JS, Images).
- `templates/`: HTML templates for the dashboard and modules.
- `docs/`: Comprehensive project documentation and Master Specs.
- `init_db.py`: Database initialization and fluid schema setup script.

## 🤝 Contributing
This project is designed to be an open-source template for BNI chapters worldwide. Contributions to improve data parsing, AI prompts, or UI components are welcome.

## 📜 License
MIT License. Feel free to use and adapt for your local chapter.

---
*Developed for BNI Mahardika Chapter.*
