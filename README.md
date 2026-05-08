# SmartAnalyticsApp

SmartAnalyticsApp is a FastAPI backend for preprocessing datasets and running unsupervised learning workflows.
## Who is this for?

- Data analysts and data scientists who want a lightweight API to preprocess data and run unsupervised learning experiments.
- Developers integrating preprocessing and unsupervised analytics into data pipelines or frontend apps.
- Students and researchers exploring unsupervised learning results through API-driven workflows.

## What is included?

- Dataset uploads and storage
- Preprocessing utilities
- Unsupervised learning endpoints (clustering, anomaly detection, association rules, and more)
- Saved outputs for diagrams and analysis artifacts

## Requirements

- Python 3.11 or newer
- uv (Python dependency management and runner)

## How to run (most important)

From the repository root:

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

The API will be available at:

- http://127.0.0.1:8000
- OpenAPI docs: http://127.0.0.1:8000/docs

## Configuration

If you need environment variables, place them in a `.env` file inside [backend/](backend/).

Example `.env`:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

## Project structure

- [backend/](backend/) - FastAPI backend and services
- [backend/routers/](backend/routers/) - API route definitions
- [backend/services/](backend/services/) - Clustering and preprocessing logic
- [backend/preprocessing/](backend/preprocessing/) - Data preprocessing utilities
- [backend/models/](backend/models/) - Model and clustering implementations