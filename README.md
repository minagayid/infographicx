# InfographicX

**AI Knowledge Visualization Platform**

Transform any input — PDFs, code repos, websites, videos, research papers — into interactive visual knowledge systems.

![InfographicX](https://img.shields.io/badge/status-active-brightgreen) ![Python](https://img.shields.io/badge/python-3.11+-blue) ![TypeScript](https://img.shields.io/badge/typescript-5.x-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## Overview

InfographicX is an AI-powered platform that ingests unstructured and structured data from diverse sources, extracts knowledge, discovers relationships and stories, and automatically generates interactive visualizations including:

- **Infographics** — rich visual summaries
- **Mind Maps** — hierarchical knowledge exploration
- **Knowledge Graphs** — entity-relationship networks
- **Timelines** — chronological event flows
- **Flowcharts** — process and decision diagrams
- **Dashboards** — metric-centric views
- **Decision Trees** — branching logic visualizations
- **Learning Paths** — progressive knowledge journeys

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      InfographicX Platform                   │
├─────────────┬──────────────┬───────────────┬────────────────┤
│  Frontend   │   Backend    │  Agent System  │   Workers      │
│  React+Vite │  FastAPI      │  7 AI Agents   │  Celery+Redis  │
└─────────────┴──────────────┴───────────────┴────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       Processing Pipeline                    │
├──────────┬──────────┬──────────┬──────────┬──────────────────┤
│  Input   │Knowledge │Relation- │  Story   │Visualization    │
│  Engine  │Extraction│ship      │Discovery │Engine           │
│          │Engine    │Engine    │Engine    │                  │
└──────────┴──────────┴──────────┴──────────┴──────────────────┘
```

## Core Engines

| Engine | Purpose |
|--------|---------|
| **Universal Input Engine** | Accepts PDF, DOCX, PPTX, CSV, XLSX, Video, Audio, Git Repo, Website, Research Paper, API, Database |
| **Knowledge Extraction Engine** | Identifies entities, processes, relationships, dependencies, events, metrics |
| **Relationship Engine** | Discovers hidden relationships between data points |
| **Story Discovery Engine** | Determines narrative structure — timelines, cause-effect, comparisons, hierarchies |
| **Visualization Engine** | Auto-selects optimal visualization type and layout |
| **Interaction Engine** | Multi-layer knowledge zoom (Google Maps for knowledge), galaxy mode |
| **Collaboration Engine** | Real-time multi-user editing with conflict resolution |
| **Presentation Engine** | Transforms infographics into presentations, websites, reports, PDFs, videos, courses |
| **Publishing Engine** | Theme selection, branding, multi-format export (HTML, PDF, PNG, SVG, PPTX, Website) |

## God's Eye — open atlas layer

God's Eye is a source-linked globe workspace for exploring real-world places without
locking the product to a proprietary map or imagery vendor. It combines:

- **OpenStreetMap** attribution-ready map context and coordinates.
- **Wikimedia Commons** location searches for community-uploaded video and imagery.
- **Internet Archive** searches for public archive footage and field recordings.
- A lightweight catalog API at `GET /api/v1/gods-eye/catalog` with region and text
  filters, plus `GET /api/v1/gods-eye/sources` for the provider/license contract.

The frontend lives in `frontend/src/App.tsx` and provides a responsive atlas view,
region filters, location pins, selected-place intelligence, and direct source/archive
links. Media is not copied or re-hosted: each result links to its original archive so
users can inspect the per-file license and attribution requirements before reuse.

## AI Agent Ecosystem

| Agent | Role |
|-------|------|
| **Extraction Agent** | Orchestrates knowledge extraction from input sources |
| **Story Agent** | Determines the best narrative structure for extracted knowledge |
| **Design Agent** | Selects visual design, themes, and layout principles |
| **Chart Agent** | Generates and optimizes chart/visualization specifications |
| **Research Agent** | Enriches knowledge with external data and context |
| **Fact Check Agent** | Validates extracted facts against reliable sources |
| **Publishing Agent** | Manages export formats, theming, and distribution |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Redis (for Celery task queue)

### Using Docker

```bash
git clone https://github.com/minagayid/infographicx.git
cd infographicx
cp .env.example .env
docker compose up --build
```

### Local Development

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend
cd backend
pytest --cov=app --cov-report=term-missing

# Frontend
cd frontend
npm run test
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
infographicx/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry
│   │   ├── core/                # Config, security, dependencies
│   │   ├── api/v1/              # REST API routes
│   │   ├── engines/             # Core processing engines
│   │   ├── agents/              # AI agent ecosystem
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic services
│   │   ├── db/                  # Database session & migrations
│   │   └── utils/               # Shared utilities
│   ├── tests/                   # Test suite
│   ├── scripts/                 # Utility scripts
│   ├── pyproject.toml           # Python project config
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── stores/              # State management (Zustand)
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API client services
│   │   ├── types/               # TypeScript types
│   │   └── styles/              # Global styles
│   ├── package.json
│   └── Dockerfile
├── docker/
│   └── docker-compose.yml
├── .github/workflows/           # CI/CD pipelines
└── README.md
```

## Environment Variables

See [.env.example](.env.example) for the full list of configuration options.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License — see [LICENSE](LICENSE) for details.
