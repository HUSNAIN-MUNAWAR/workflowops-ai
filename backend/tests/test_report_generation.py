from app.reports.generator import generate_report_pack


def test_report_generation(tmp_path):
    paths = generate_report_pack("Demo Report", {"status": "ok"}, tmp_path, "demo")
    assert "json" in paths and "markdown" in paths and "html" in paths
