from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import datetime
import sys
from pathlib import Path

# Make src importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import existing pipeline logic
from unihack.part1_foundation.data_loader import load_part1_data
from unihack.part2_classification.pipeline import run_part2
from unihack.part3_normalization.pipeline import run_part3_from_part2
from unihack.part4_enrichment_qa.pipeline import run_part4_from_part3

app = FastAPI(title="ForgeIQ API", description="REST API for the ForgeIQ Pipeline")

# Allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory state
class PipelineState:
    def __init__(self):
        self.status = "idle" # idle, running, completed, error
        self.current_stage = None
        self.part1_count = 0
        self.part2_count = 0
        self.part3_count = 0
        self.part4_count = 0
        self.started_at = None
        self.completed_at = None
        self.error = None
        self.results: List[Dict[str, Any]] = []

state = PipelineState()

def execute_pipeline():
    global state
    state.status = "running"
    state.current_stage = "part1"
    state.part1_count = 0
    state.part2_count = 0
    state.part3_count = 0
    state.part4_count = 0
    state.started_at = datetime.datetime.utcnow().isoformat()
    state.completed_at = None
    state.error = None
    state.results = []
    
    try:
        # Part 1
        part1_data = load_part1_data()
        state.part1_count = len(part1_data.sample_input) if hasattr(part1_data, "sample_input") else 0
        
        # Part 2
        state.current_stage = "part2"
        part2_results = run_part2(part1_data)
        state.part2_count = len(part2_results)
        
        # Part 3
        state.current_stage = "part3"
        part3_results = run_part3_from_part2(part2_results=part2_results, part1_data=part1_data)
        state.part3_count = len(part3_results)
        
        # Part 4
        state.current_stage = "part4"
        required_attributes = ["manufacturer", "brand"]
        part4_results = run_part4_from_part3(part3_results, required_attributes=required_attributes)
        
        # In Part 4, results are lists of dicts
        # Ensure they have an ID for frontend tracking if not present
        results_with_ids = []
        for res in part4_results:
            if isinstance(res, dict):
                # We use MPN as an ID or generate one
                if "id" not in res:
                    res["id"] = str(uuid.uuid4())
                results_with_ids.append(res)
            else:
                # Fallback if not dict (should be dict from Part 4)
                results_with_ids.append({"id": str(uuid.uuid4()), "data": str(res)})
                
        state.part4_count = len(results_with_ids)
        state.results = results_with_ids
        
        state.status = "completed"
        state.current_stage = None
        state.completed_at = datetime.datetime.utcnow().isoformat()
        
    except Exception as e:
        state.status = "error"
        state.error = str(e)
        state.current_stage = None
        state.completed_at = datetime.datetime.utcnow().isoformat()

@app.post("/api/pipeline/run", status_code=202)
async def run_pipeline(background_tasks: BackgroundTasks):
    if state.status == "running":
        raise HTTPException(status_code=400, detail="Pipeline is already running")
    
    background_tasks.add_task(execute_pipeline)
    return {"message": "Pipeline execution started"}

@app.get("/api/pipeline/status")
async def get_pipeline_status():
    return {
        "status": state.status,
        "current_stage": state.current_stage,
        "part1_count": state.part1_count,
        "part2_count": state.part2_count,
        "part3_count": state.part3_count,
        "part4_count": state.part4_count,
        "started_at": state.started_at,
        "completed_at": state.completed_at,
        "error": state.error
    }

@app.get("/api/products")
async def get_products():
    return {"products": state.results}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    for p in state.results:
        if p.get("id") == product_id or str(p.get("mpn")) == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/api/qa/summary")
async def get_qa_summary():
    if not state.results:
        return {
            "total_products": 0,
            "passed": 0,
            "review": 0,
            "failed": 0,
            "high_severity": 0,
            "medium_severity": 0,
            "low_severity": 0
        }
    
    passed = 0
    review = 0
    failed = 0
    high_sev = 0
    med_sev = 0
    low_sev = 0
    
    for r in state.results:
        status = r.get("part4_status", "").lower()
        if status == "passed":
            passed += 1
        elif status == "review":
            review += 1
        elif status == "failed":
            failed += 1
            
        violations = r.get("part4_violations", [])
        for v in violations:
            sev = v.get("severity", "").lower()
            if sev == "high":
                high_sev += 1
            elif sev == "medium":
                med_sev += 1
            elif sev == "low":
                low_sev += 1
                
    return {
        "total_products": len(state.results),
        "passed": passed,
        "review": review,
        "failed": failed,
        "high_severity": high_sev,
        "medium_severity": med_sev,
        "low_severity": low_sev
    }

@app.get("/api/qa/reviews")
async def get_qa_reviews():
    reviews = []
    for r in state.results:
        status = r.get("part4_status", "").lower()
        if status in ["review", "failed"]:
            violations = r.get("part4_violations", [])
            # Determine highest severity
            highest_sev = "low"
            for v in violations:
                if v.get("severity", "").lower() == "high":
                    highest_sev = "high"
                elif v.get("severity", "").lower() == "medium" and highest_sev != "high":
                    highest_sev = "medium"
                    
            reviews.append({
                "id": r.get("id"),
                "mpn": r.get("mpn"),
                "manufacturer": r.get("manufacturer"),
                "issue_count": len(violations),
                "highest_severity": highest_sev,
                "confidence": r.get("confidence", 0.0)
            })
            
    return reviews

from fastapi.responses import JSONResponse, Response
import csv
import io

@app.get("/api/pipeline/export")
async def export_pipeline(format: str = 'csv'):
    if format.lower() == 'json':
        return JSONResponse(content=state.results)
    
    # Default to CSV
    if not state.results:
        return Response(content="", media_type="text/csv")
        
    output = io.StringIO()
    # Get all keys from the first dictionary to act as headers
    keys = list(state.results[0].keys())
    
    writer = csv.DictWriter(output, fieldnames=keys)
    writer.writeheader()
    for row in state.results:
        # Convert complex objects to strings for CSV
        csv_row = {}
        for k, v in row.items():
            if isinstance(v, (list, dict)):
                csv_row[k] = str(v)
            else:
                csv_row[k] = v
        writer.writerow(csv_row)
        
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=forgeiq_export.csv"}
    )

