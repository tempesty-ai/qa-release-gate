from gate.release_gate import decide_gate


def test_no_go_when_open_p1_exists() -> None:
    release = {
        "change_scope": [],
        "automation_coverage": {"overall": 90, "critical_flow": 90, "changed_area": 90, "manual_supplement_done": True},
        "quality_signals": {},
        "business_window": {"monitoring_owner_ready": True, "rollback_plan_ready": True, "rollback_tested": True},
        "release_readiness": {"qa_signoff_ready": True, "operations_approval": True, "known_issues_documented": True}
    }
    defects = [{"id": "BUG-1", "title": "payment blocked", "severity": "P1", "status": "open"}]
    tests = []

    result = decide_gate(release, defects, tests)

    assert result.status == "NO_GO"


def test_conditional_go_for_medium_risk() -> None:
    release = {
        "change_scope": [
            {"area": "auth", "criticality": "high", "change_size": "medium"}
        ],
        "automation_coverage": {"overall": 76, "critical_flow": 72, "changed_area": 70, "manual_supplement_done": True},
        "quality_signals": {},
        "business_window": {"monitoring_owner_ready": True, "rollback_plan_ready": True, "rollback_tested": True},
        "release_readiness": {"qa_signoff_ready": False, "operations_approval": True, "known_issues_documented": True}
    }
    defects = [{"id": "BUG-2", "title": "minor auth issue", "severity": "P2", "status": "open", "customer_impact": "medium"}]
    tests = []

    result = decide_gate(release, defects, tests)

    assert result.status == "CONDITIONAL_GO"


def test_go_for_low_risk_release() -> None:
    release = {
        "change_scope": [
            {"area": "catalog", "criticality": "low", "change_size": "small"}
        ],
        "automation_coverage": {"overall": 90, "critical_flow": 88, "changed_area": 86, "manual_supplement_done": True},
        "quality_signals": {},
        "business_window": {"monitoring_owner_ready": True, "rollback_plan_ready": True, "rollback_tested": True},
        "release_readiness": {"qa_signoff_ready": True, "operations_approval": True, "known_issues_documented": True}
    }
    defects = []
    tests = []

    result = decide_gate(release, defects, tests)

    assert result.status == "GO"
