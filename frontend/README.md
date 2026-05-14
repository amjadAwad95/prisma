# Smart Analytics Data Mining Platform

A production-ready Next.js frontend for a Smart Analytics Data Mining Platform. The app lets users upload datasets, detect compatible mining algorithms, run API-backed workflows, visualize results, render base64 diagrams, and generate markdown reports.

## Tech stack

- Next.js App Router + React + TypeScript
- TailwindCSS with shadcn-style UI primitives
- Framer Motion animations
- Zustand session state
- TanStack Query for API mutations/caching
- next-themes dark/light mode
- Recharts visualizations
- react-markdown and syntax-highlighted code blocks
- Sonner toast notifications

## Getting started

```bash
cp .env.example .env.local
npm install
npm run dev
```

Then open `http://localhost:3000`.

Set the backend base URL in `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

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

## API integration

The API layer lives in `src/services/api.ts` and implements:

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

## Session persistence

State is persisted with Zustand into `sessionStorage` as the source of truth and mirrored to `localStorage` during the active browser session. On a new browser session, stale `localStorage` snapshots are removed automatically by `ensureSessionBoundary()`.

Stored session data includes:

- active upload ID and dataset metadata
- compatible algorithm methods
- algorithm outputs and diagram metadata
- recent upload history
- report inputs derived from previous results

## Notes

- Association tables use polished preview rows because the provided API returns file paths, not parsed file contents.
- Chart previews remain visible before running an algorithm to avoid empty dashboard dead zones.
- Browser print is used for PDF export, which keeps the app dependency-light and allows users to save a styled PDF from the print dialog.
