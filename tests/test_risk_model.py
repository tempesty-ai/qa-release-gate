from gate.risk_model import calculate_risk_score


def test_calculate_risk_score_caps_at_100() -> None:
    release = {
        "change_scope": [
            {"area": "payment", "criticality": "critical", "change_size": "large"}
        ],
        "automation_coverage": {"overall": 40, "critical_flow": 30}
    }
    defects = [
        {
            "id": "BUG-1",
            "title": "critical issue",
            "severity": "P1",
            "status": "open",
            "workaround": "false",
            "reopened": "true"
        },
        {
            "id": "BUG-2",
            "title": "major issue",
            "severity": "P2",
            "status": "open",
            "workaround": "false",
            "reopened": "true"
        }
    ]
    tests = [
        {"id": "TC-1", "case_name": "checkout", "area": "payment", "criticality": "critical", "status": "failed"}
    ]

    score, risks = calculate_risk_score(release, defects, tests)

    assert score == 100
    assert risks[0].points >= risks[-1].points


def test_resolved_defects_do_not_add_risk() -> None:
    release = {"change_scope": [], "automation_coverage": {"overall": 90, "critical_flow": 90}}
    defects = [{"id": "BUG-1", "severity": "P1", "status": "resolved"}]
    tests = []

    score, risks = calculate_risk_score(release, defects, tests)

    assert score == 0
    assert risks == []

