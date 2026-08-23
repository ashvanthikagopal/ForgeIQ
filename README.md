# ⚡ ForgeIQ

> **AI-Powered Industrial Product Content Enrichment & Quality Assurance Platform**

ForgeIQ transforms raw, messy, and incomplete industrial product catalog data into structured, normalized, validated, and commerce-ready product information.

---

## 🌟 Key Features

- **Multi-Stage Processing Pipeline**: Seamlessly guides catalog data through 4 stages: Foundation Input Analysis $\rightarrow$ Taxonomy Classification & Attribute Extraction $\rightarrow$ Normalization & Description Generation $\rightarrow$ Enrichment & Quality Assurance (QA).
- **Intelligent Taxonomy Classifier**: High-precision taxonomy matching featuring stemmed token matching, leaf-segment weighting, domain keyword fallback, and Gemini LLM integration for ambiguous product entries.
- **Rule-Based Attribute Extractor**: Extracts structured attribute-value pairs (e.g., *Mount Type*, *Finish*, *Material*, *Dimensions*) from unstructured text using word-boundary pattern matching.
- **Automated Normalization Engine**: Standardizes Unit of Measure (UOM) abbreviations, converts decimal/fraction formats, and cleans brand and manufacturer names.
- **Commerce-Ready Description Builder**: Generates 4 compliant product description formats:
  - 📄 **Invoice Description**: ALL-CAPS, strictly $\le$ 40 characters.
  - 📱 **Mobile Description**: Concise, structured, $\le$ 80 characters.
  - 🏷️ **Product Title**: Standardized format incorporating Brand, Leaf Category, and MPN.
  - 📝 **Long Description & Marketing Copy**: Rich product summaries optimized for e-commerce.
- **QA & Review Queue System**: Automated quality validation checking character limits, casing, LOV values, and placeholder compliance with confidence scoring.
- **Interactive E-Commerce Interface**: Modern React dashboard with live pipeline execution tracking, search & filter controls, QA review queue, and CSV exports.

---

## 🏗️ Architecture & Pipeline Stages

```
Input CSV / Excel 
      │
      ▼
[Stage 1: Part 1 Foundation] ──► Parse, header mapping, missing value & placeholder detection
      │
      ▼
[Stage 2: Part 2 Classification] ──► Taxonomy classification & structured attribute extraction
      │
      ▼
[Stage 3: Part 3 Normalization] ──► UOM normalization, title & 4-format description generation
      │
      ▼
[Stage 4: Part 4 Enrichment & QA] ──► Rule validation, confidence scoring & review queue routing
      │
      ▼
Enriched Commerce-Ready Catalog (CSV Export / API)
```

---

## 🛠️ Technology Stack

### **Backend**
- **Framework**: Python 3.10+ / FastAPI / Uvicorn
- **Data & ML**: Pandas, OpenPyXL, Pydantic, Google GenAI SDK (`google-genai`)
- **Testing**: Pytest (45 unit & integration tests)

### **Frontend**
- **Framework**: React 19 / Vite / React Router DOM v7
- **Styling**: TailwindCSS v4 / Vanilla CSS
- **Icons & Visualization**: Lucide React, Recharts
- **HTTP Client**: Axios

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm

---

### 1. Backend Setup (FastAPI)

1. **Navigate to the project root directory**:
   ```powershell
   cd ForgeIQ
   ```

2. **Create & activate virtual environment** *(optional but recommended)*:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Start the FastAPI backend server**:
   ```powershell
   python server.py
   ```
   *or using Uvicorn directly:*
   ```powershell
   python -m uvicorn server:app --reload
   ```

   > 📌 **Backend API**: `http://localhost:8000`  
   > 📌 **Interactive API Docs**: `http://localhost:8000/docs`

---

### 2. Frontend Setup (React + Vite)

1. **Open a new terminal and navigate to the `frontend` folder**:
   ```powershell
   cd frontend
   ```

2. **Install Node dependencies**:
   ```powershell
   npm install
   ```

3. **Start the Vite development server**:
   ```powershell
   npm run dev
   ```

   > 📌 **Frontend Application**: `http://localhost:5173`

---

## 🧪 Running Unit & Integration Tests

Run the complete test suite across all 4 pipeline stages using `pytest`:

```powershell
python -m pytest
```

---

## 📊 API Reference Overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | `GET` | Health check & pipeline status summary |
| `/api/pipeline/run` | `POST` | Trigger pipeline execution (sample dataset or custom CSV upload) |
| `/api/pipeline/status` | `GET` | Retrieve live progress & current stage execution details |
| `/api/products` | `GET` | Paginated product catalog with filtering (search, status, manufacturer, classpath) |
| `/api/products/{id}` | `GET` | Retrieve full product details & enrichment metadata |
| `/api/qa/summary` | `GET` | QA evaluation metrics (pass rates, review queues, severity breakdowns) |
| `/api/pipeline/export` | `GET` | Export enriched product catalog as CSV |

---

## 📁 Directory Structure

```
ForgeIQ/
├── data/                       # Ground truth and sample datasets
├── frontend/                   # React + Vite frontend application
│   ├── src/
│   │   ├── components/         # Dashboard, pipeline, QA review components
│   │   ├── context/            # Pipeline state & toast context providers
│   │   ├── pages/              # Application views & pages
│   │   └── services/           # Axios API client functions
│   └── package.json
├── src/unihack/                # Core Python pipeline modules
│   ├── part1_foundation/       # Data loader, parsers & ground truth harness
│   ├── part2_classification/   # Taxonomy classifier & attribute extractor
│   ├── part3_normalization/    # UOM lookup, description builder & normalizer
│   └── part4_enrichment_qa/    # QA validation, confidence scorer & packager
├── tests/                      # Automated unit & integration tests
├── server.py                   # FastAPI backend REST API server
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 📄 License

This project is developed for the UniHack Hackathon Challenge.
