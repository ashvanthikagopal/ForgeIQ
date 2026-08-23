import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data

def test_api_pipeline_status():
    response = client.get("/api/pipeline/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "part1_count" in data

def test_api_products():
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total" in data
    assert len(data["products"]) > 0

def test_api_product_details():
    # Fetch first product
    products_res = client.get("/api/products?limit=1")
    products = products_res.json()["products"]
    assert len(products) > 0
    first_id = products[0]["id"]

    response = client.get(f"/api/products/{first_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == first_id

def test_api_product_violations_and_confidence():
    products_res = client.get("/api/products?limit=1")
    products = products_res.json()["products"]
    first_id = products[0]["id"]

    violations_res = client.get(f"/api/products/{first_id}/violations")
    assert violations_res.status_code == 200
    assert isinstance(violations_res.json(), list)

    confidence_res = client.get(f"/api/products/{first_id}/confidence")
    assert confidence_res.status_code == 200
    assert "part4_confidence" in confidence_res.json()

def test_api_qa_reviews_and_metrics():
    reviews_res = client.get("/api/products/review")
    assert reviews_res.status_code == 200
    assert isinstance(reviews_res.json(), list)

    metrics_res = client.get("/api/metrics")
    assert metrics_res.status_code == 200
    metrics_data = metrics_res.json()
    assert "total_products" in metrics_data
    assert "passed" in metrics_data
    assert "review" in metrics_data

def test_api_export():
    export_csv = client.get("/api/pipeline/export?format=csv")
    assert export_csv.status_code == 200
    assert "text/csv" in export_csv.headers["content-type"]

    export_json = client.get("/api/pipeline/export?format=json")
    assert export_json.status_code == 200
    assert "application/json" in export_json.headers["content-type"]

def test_api_intelligence_endpoints():
    res_cls = client.get("/api/classification")
    assert res_cls.status_code == 200
    assert "total_classified" in res_cls.json()

    res_attr = client.get("/api/attributes")
    assert res_attr.status_code == 200
    assert "total_extracted" in res_attr.json()

    res_norm = client.get("/api/normalization")
    assert res_norm.status_code == 200
    assert "total_uom_normalized" in res_norm.json()

    res_desc = client.get("/api/descriptions")
    assert res_desc.status_code == 200
    assert "invoice_limit" in res_desc.json()

    res_enr = client.get("/api/enrichment")
    assert res_enr.status_code == 200
    assert "total_enriched_fields" in res_enr.json()


