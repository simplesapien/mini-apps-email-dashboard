import json
import re
from pathlib import Path

root = Path(__file__).parent
data = json.loads((root / "data.json").read_text())
page = (root / "index.html").read_text()

assert len(data["reports"]) == 6
assert len({report["key"] for report in data["reports"]}) == 6
assert all(report["report_through"] == data["common_cutoff"] for report in data["reports"])

for report in data["reports"]:
    delivered = report["delivered"]
    assert 0 <= report["human_clicks"] <= delivered
    assert 0 <= report["website_visitors"] <= delivered
    assert 0 <= report["app_visitors"] <= delivered
    assert 0 <= report["engaged_users"] <= delivered
    assert all(app["visited"] <= delivered and app["engaged"] <= delivered for app in report["apps"])
    assert f"{report['human_clicks']} of {delivered}" in page
    assert f"{report['website_visitors']} of {delivered}" in page

for cohort in data["lift"]["cohorts"]:
    recipients = cohort["recipients"]
    for name in ("website_visitors", "mini_app_visitors", "engaged_users"):
        metric = cohort[name]
        for period in ("pre", "post"):
            expected = round(metric[period]["count"] / recipients * 100, 1)
            assert metric[period]["rate_pct"] == expected
        expected_change = round(
            (metric["post"]["count"] - metric["pre"]["count"]) / recipients * 100, 1
        )
        assert metric["absolute_change_pp"] == expected_change

public_text = (root / "data.json").read_text() + page
assert not re.search(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    public_text,
    re.IGNORECASE,
)
assert not re.search(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    public_text,
    re.IGNORECASE,
)

print("Dashboard data and privacy checks passed.")
