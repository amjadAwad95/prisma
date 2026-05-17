# PRISMA

PRISMA is a full-stack smart analytics platform with a FastAPI backend and a Next.js frontend. It lets users upload datasets, detect compatible mining algorithms, run workflows, visualize results, and generate markdown reports.

## Demo Video

Watch the walkthrough: 


https://github.com/user-attachments/assets/23f5774b-f83b-454f-950c-3ddeaeb18445



---

## Who is this for?

- Data analysts and data scientists who want a lightweight platform to preprocess data and run unsupervised learning experiments.
- Developers integrating preprocessing and analytics into data pipelines or frontend apps.
- Students and researchers exploring unsupervised learning results through API-driven workflows.

## What is included?

- Dataset uploads and metadata storage
- Preprocessing utilities
- Unsupervised learning workflows (clustering, association, PCA, time series)
- Reports and saved artifacts (diagrams, charts, analysis outputs)
- Dashboard UI, algorithm catalog, and documentation pages

## Requirements

- Python 3.11 or newer
- uv (Python dependency management and runner)
- Node.js (LTS recommended) and npm

## How to run (most important)

### 1) Backend API

From the repository root:

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

The API will be available at:

- http://127.0.0.1:8000
- OpenAPI docs: http://127.0.0.1:8000/docs

### 2) Frontend UI

From the repository root:

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the app:

```bash
npm run dev
```

The UI will be available at http://localhost:3000.

## Configuration

Backend environment variables live in `backend/.env`.

Example:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

Frontend environment variables live in `frontend/.env.local`.

## Main routes

- `/` landing page
- `/dashboard` upload and workspace dashboard
- `/algorithms` algorithm catalog
- `/algorithms/clustering`
- `/algorithms/association`
- `/algorithms/pca`
- `/algorithms/time-series`
- `/reports`
- `/documentation`

## API endpoints

- `POST /files/upload`
- `GET /files/metadata/{upload_id}`
- `GET /files/metadata`
- `GET /files/diagrams/{upload_id}/{diagram_type}`
- `GET /preprocessing/type/{upload_id}`
- `POST /preprocessing/run`
- `POST /clustering/run`
- `POST /clustering/best`
- `POST /association/run`
- `POST /pca/run`
- `POST /time-series/run`
- `POST /reports/generate`

## Project structure

- [backend/](backend/) - FastAPI backend and services
- [backend/routers/](backend/routers/) - API route definitions
- [backend/services/](backend/services/) - Analytics services
- [backend/preprocessing/](backend/preprocessing/) - Data preprocessing utilities
- [backend/models/](backend/models/) - Model implementations
- [frontend/](frontend/) - Next.js frontend
- [frontend/src/app/](frontend/src/app/) - App Router routes and layout
- [frontend/src/components/](frontend/src/components/) - UI components
- [frontend/src/services/](frontend/src/services/) - API client
