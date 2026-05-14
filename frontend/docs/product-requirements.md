You are an elite senior frontend engineer and UI/UX designer.
Build a production-level, modern, visually stunning, responsive web application for a **Smart Analytics Data Mining Platform**.

The platform allows users to upload datasets, automatically analyze them, determine which data mining algorithms are applicable, run algorithms, visualize results, and generate intelligent reports.

The UI/UX quality should feel like a premium SaaS analytics platform similar to Stripe, Vercel, Notion, or Databricks.

---

# Tech Stack Requirements

Use:

* React + TypeScript
* Next.js (latest app router)
* TailwindCSS
* Framer Motion
* Shadcn/UI components
* Lucide React icons
* Zustand or Context API for state management
* React Query / TanStack Query for API calls and caching
* next-themes for dark/light mode
* Recharts or Chart.js for charts
* react-markdown for markdown rendering

The website must be:

* Fully responsive
* Smooth animated
* Accessible
* Clean architecture
* Component-driven
* Beautiful in both dark and light modes

---

# Design Style

The website should look futuristic and professional.

Style inspiration:

* Vercel
* Linear
* Notion
* Databricks
* Framer
* Stripe Dashboard

Use:

* Glassmorphism
* Gradient accents
* Soft shadows
* Subtle hover animations
* Animated cards
* Elegant typography
* Smooth transitions
* Clean spacing
* Premium dashboard aesthetics

Add:

* Dark mode toggle
* Light mode toggle
* Animated background gradients
* Floating particles/grid effects
* Loading skeletons
* Toast notifications
* Empty states
* Error states
* Animated charts

---

# Website Structure

Create the following pages:

## 1. Landing Page (/)

This should be a premium hero landing page.

Sections:

* Hero section
* Features section
* Supported algorithms section
* How it works section
* Interactive analytics preview
* CTA section
* Footer

Hero section should include:

* Big headline
* Subtitle
* Animated background
* Upload CTA button
* Dashboard preview image/mockup
* Smooth scroll animations

Navbar/Header:

* Logo
* Home
* Dashboard
* Algorithms
* Reports
* Documentation
* Theme toggle
* Upload Dataset button

Footer:

* Social links
* GitHub
* Documentation
* About project
* Contact

---

# Core Dashboard Features

## Main Dashboard Page (/dashboard)

The dashboard is the main workspace.

Features:

* Upload dataset area
* Dataset metadata panel
* Available algorithms panel
* Session history
* Recent analyses
* Statistics cards
* Charts and visual summaries

Use drag-and-drop upload.

Supported file types:

* CSV
* XLSX
* JSON

Show:

* filename
* file size
* upload date
* dataset preview
* detected columns
* supported algorithms

---

# API Integration

Base URL should be configurable using environment variables.

Example:
NEXT_PUBLIC_API_URL=http://localhost:8000

Create a complete API service layer.

---

# Upload Flow

When a user uploads a file:

POST:
`/files/upload`

The response returns:

* upload_id
* filename
* metadata
* allowed method_types

Immediately after upload:

* Save upload_id
* Save session data in localStorage
* Persist algorithm results in localStorage
* Remove all stored session data when browser session ends

Use session-based persistence.

---

# Smart Algorithm Enable/Disable Logic

After upload:
Call:

GET:
`/preprocessing/type/{upload_id}`

This endpoint returns allowed algorithms.

Based on response:
Enable or disable algorithm cards/buttons dynamically.

Supported algorithm categories:

* Clustering
* Association Rule Mining
* PCA
* Time Series Forecasting

Disabled algorithms should:

* Appear visually disabled
* Show tooltip explaining incompatibility
* Animate on hover if enabled

---

# Algorithm Pages

Each algorithm must have its own dedicated page.

Create:

* /algorithms/clustering
* /algorithms/association
* /algorithms/pca
* /algorithms/time-series

Each page should include:

* Explanation section
* Interactive parameter controls
* Run algorithm button
* Results visualization
* Metrics cards
* Generated diagrams
* Export/report options

---

# Clustering Page

Use:
POST `/clustering/run`

Allow selecting:

* KMeans
* DBSCAN
* Hierarchical

Also implement:
POST `/clustering/best`

Show:

* silhouette score
* number of clusters
* noise points
* best algorithm comparison table
* cluster visualizations
* animated charts

Fetch diagrams from:
GET `/files/diagrams/{upload_id}/{diagram_type}`

The API returns base64 images.

Render them beautifully inside:

* carousels
* expandable modals
* lightbox viewer

---

# PCA Page

Use:
POST `/pca/run`

Allow:

* number of components
* threshold controls

Show:

* explained variance ratio
* cumulative variance
* scree plot
* variance charts
* transformed dataset preview

Beautiful animated visualizations required.

---

# Association Rule Mining Page

Use:
POST `/association/run`

Controls:

* min support
* min confidence
* min lift

Show:

* frequent itemsets
* association rules
* confidence metrics
* lift metrics
* rule visualizations
* interactive tables

---

# Time Series Page

Use:
POST `/time-series/run`

Allow:

* Linear Regression
* ARIMA

Show:

* forecasting charts
* historical trends
* metrics
* predicted values
* target column
* datetime column

Visualize:

* historical plot
* forecast plot

Use highly polished charts.

---

# Diagrams Handling

The diagrams endpoint returns images in base64.

Requirements:

* Convert and render correctly
* Support multiple diagrams
* Lazy load images
* Fullscreen preview modal
* Download image option

---

# Report Generation

Create a Reports page:
`/reports`

Use:
POST `/reports/generate`

The report endpoint returns markdown.

Requirements:

* Collect all algorithm outputs from localStorage/session
* Send them to report API
* Render markdown beautifully
* Add:

  * table styling
  * syntax highlighting
  * code block rendering
  * export to PDF
  * export to markdown
  * print support

Report UI should feel like:

* Notion
* ChatGPT reports
* Research papers

---

# State Management

Implement proper architecture:

* API layer
* Hooks
* Reusable components
* Error boundaries
* Global loading states
* Persistent session state

Store:

* upload_id
* algorithm results
* generated diagrams
* report inputs

Use localStorage/sessionStorage intelligently.

Clear storage automatically when session ends.

---

# Components To Create

Create reusable components:

* Navbar
* Sidebar
* UploadDropzone
* AlgorithmCard
* MetricCard
* AnimatedChartCard
* DatasetPreviewTable
* MarkdownReportViewer
* DiagramGallery
* ThemeToggle
* LoadingSkeleton
* ErrorState
* EmptyState
* FloatingActionButtons
* SessionHistoryPanel

---

# Animations

Use Framer Motion extensively:

* Page transitions
* Card hover effects
* Fade-ins
* Stagger animations
* Loading animations
* Chart animations
* Scroll-triggered animations

---

# User Experience Requirements

The UX should feel extremely polished.

Include:

* optimistic UI
* progress bars
* upload progress
* retry mechanisms
* toast notifications
* keyboard accessibility
* responsive mobile layouts
* smooth transitions

---

# Error Handling

Handle:

* API failures
* invalid files
* unsupported datasets
* timeout errors
* missing diagrams
* malformed markdown

Show elegant error messages.

---

# Code Quality Requirements

Generate:

* clean architecture
* scalable folder structure
* reusable hooks
* typed DTOs/interfaces
* proper API clients
* environment configuration
* comments where necessary

Use best practices everywhere.

---

# Suggested Folder Structure

/src
/app
/components
/features
/services
/hooks
/types
/store
/utils
/styles

---

# Important Functional Requirements

1. Every algorithm has its own page.
2. Algorithms must dynamically enable/disable based on preprocessing endpoint.
3. Results must persist during the session.
4. Session data must clear after session ends.
5. Report generation must aggregate all previous results.
6. Diagrams must render from base64 responses.
7. Dark/light mode must work globally.
8. UI must feel premium and modern.
9. Entire app must be fully responsive.
10. Use realistic mock analytics visuals where needed.

---

# API Endpoints

## Upload File

POST `/files/upload`

## Get Metadata

GET `/files/metadata/{upload_id}`

## List Metadata

GET `/files/metadata`

## Get Diagrams

GET `/files/diagrams/{upload_id}/{diagram_type}`

## Get Allowed Methods

GET `/preprocessing/type/{upload_id}`

## Run Preprocessing

POST `/preprocessing/run`

## Run Clustering

POST `/clustering/run`

## Run Best Clustering

POST `/clustering/best`

## Run Association Mining

POST `/association/run`

## Run PCA

POST `/pca/run`

## Run Time Series

POST `/time-series/run`

## Generate Report

POST `/reports/generate`

---

# Expected Output

Generate:

* Complete frontend application
* Beautiful UI
* Fully functional API integration
* Reusable architecture
* Responsive design
* Dark/light theme
* Production-ready code

The final result should look like a high-end AI analytics SaaS platform.
