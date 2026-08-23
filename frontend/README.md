# ForgeIQ Frontend

> **Product Content Enrichment & Quality Assurance Platform**  
> *Enrich. Normalize. Validate. Deliver.*

ForgeIQ is an enterprise React + Vite web interface built to monitor, trigger, and inspect the Python Product Content Enrichment & Quality Assurance pipeline across all 4 processing stages.

---

## 🚀 Quick Start

### 1. Backend Setup

Ensure Python dependencies are installed and start the FastAPI REST API server:

```bash
# In project root:
pip install -r requirements.txt
python -m uvicorn server:app --port 8000 --reload
```

The REST API will be served at `http://localhost:8000/api`.

### 2. Frontend Installation & Development

```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

The frontend will run at `http://localhost:5173`.

### 3. Production Build & Preview

```bash
# Create optimized production build
npm run build

# Preview production build locally
npm run preview
```

---

## ⚙️ Environment Configuration

Set the backend API endpoint URL in `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## 🔌 API Endpoints Contract

The frontend consumes these REST endpoints provided by `server.py`:

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/pipeline/run` | Triggers full execution of Parts 1–4 Python pipeline |
| `GET` | `/api/pipeline/status` | Returns pipeline status and stage product counts |
| `GET` | `/api/products` | Paginated product list with search and filter parameters |
| `GET` | `/api/products/{id}` | Complete detailed inspection data for a single product |
| `GET` | `/api/qa/summary` | QA statistics summary (Passed, Review, Failed, Severities) |
| `GET` | `/api/qa/reviews` | Queue of products requiring QA review |
| `GET` | `/api/pipeline/results` | Returns final Part 4 output dataset |
| `GET` | `/api/pipeline/export` | Downloads catalog data as CSV (`format=csv`) or JSON (`format=json`) |

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/       # Sidebar, Navbar, AppLayout
│   │   ├── dashboard/    # MetricCard, PipelineOverview, QAOverview
│   │   ├── pipeline/     # PipelineStage, PipelineFlow, PipelineProgress
│   │   ├── products/     # ProductTable, ProductFilters, ProductRow, ProductStatusBadge
│   │   ├── product/      # Stage detail cards (Part 1, 2, 3, 4) & QAViolations
│   │   ├── qa/           # QAReviewList, QAIssueCard, SeverityBadge
│   │   ├── analytics/    # QAStatusChart, PipelineChart, SeverityChart, ReviewReasonsChart
│   │   └── common/       # Card, Button, Badge, Modal, Skeleton, ErrorState
│   ├── pages/            # Dashboard, Pipeline, Products, ProductDetails, QAReview, Analytics, Settings
│   ├── services/         # Centralized Axios API service layer (api.js)
│   ├── context/          # PipelineContext state management
│   ├── hooks/            # usePipeline, useProducts, useQA
│   └── utils/            # formatters, status styles, error handlers
├── package.json
├── vite.config.js
└── README.md
```

---

## 🛠️ Troubleshooting

- **Backend Offline Error**: Verify `python -m uvicorn server:app --port 8000` is running on port 8000. Use the **Test Backend Connection** button in Settings.
- **Port Conflict**: If port 8000 is occupied, terminate existing python uvicorn processes or release the port.
