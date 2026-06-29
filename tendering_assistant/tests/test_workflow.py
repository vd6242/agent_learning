from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_opportunity():
    resp = client.post(
        "/opportunities",
        json={"title": "500kVA DG Set Supply", "customer": "Acme Power", "project_type": "dg_set"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["stage"] == "opportunity_identified"
    assert body["id"].startswith("opp_")


def test_get_missing_opportunity_404():
    resp = client.get("/opportunities/does-not-exist")
    assert resp.status_code == 404


def test_upload_document_requires_existing_opportunity():
    resp = client.post(
        "/opportunities/does-not-exist/documents",
        files={"file": ("rfp.txt", b"some tender text", "text/plain")},
    )
    assert resp.status_code == 404


def test_upload_and_analyze_requires_llm_config():
    create = client.post(
        "/opportunities",
        json={"title": "BOP Package", "customer": "Voltaic Co", "project_type": "bop"},
    )
    opp_id = create.json()["id"]

    upload = client.post(
        f"/opportunities/{opp_id}/documents",
        files={"file": ("rfp.txt", b"Tender for BOP works. Deadline: 2026-09-01.", "text/plain")},
    )
    assert upload.status_code == 201
    doc_id = upload.json()["id"]

    analyze = client.post(f"/documents/{doc_id}/analyze")
    # No ANTHROPIC_API_KEY configured in test env -> provider raises a clear
    # configuration error rather than an opaque failure.
    assert analyze.status_code == 503
    assert "ANTHROPIC_API_KEY" in analyze.json()["detail"]


def test_discovery_sources_all_unconfigured_by_default():
    resp = client.get("/discovery/sources")
    assert resp.status_code == 200
    sources = resp.json()
    assert {s["source"] for s in sources} == {
        "gem",
        "cppp_eprocure",
        "state_procurement",
        "psu_portal",
        "railways",
        "defence",
    }
    assert all(s["configured"] is False for s in sources)


def test_discovery_scan_with_no_configured_sources_returns_empty():
    resp = client.post("/discovery/scan")
    assert resp.status_code == 200
    body = resp.json()
    assert body["new_tenders"] == []
    assert body["sources_scanned"] == []
    assert len(body["sources_skipped_unconfigured"]) == 6


def test_discovery_dismiss_missing_tender_404():
    resp = client.post("/discovery/tenders/does-not-exist/dismiss")
    assert resp.status_code == 404


def test_discovery_convert_missing_tender_404():
    resp = client.post(
        "/discovery/tenders/does-not-exist/convert", json={"reviewer": "alice"}
    )
    assert resp.status_code == 404
