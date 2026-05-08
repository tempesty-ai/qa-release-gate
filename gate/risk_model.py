from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskItem:
    category: str
    points: int
    reason: str


SEVERITY_POINTS = {
    "P1": 40,
    "P2": 15,
    "P3": 5
}

CRITICAL_TEST_POINTS = {
    "critical": 20,
    "high": 12,
    "medium": 6,
    "low": 3
}

AREA_POINTS = {
    "critical": 15,
    "high": 10,
    "medium": 5,
    "low": 2
}


def score_open_defects(defects: list[dict[str, str]]) -> list[RiskItem]:
    items: list[RiskItem] = []
    for defect in defects:
        if defect.get("status") != "open":
            continue

        severity = defect.get("severity", "")
        points = SEVERITY_POINTS.get(severity, 0)
        if defect.get("reopened") == "true":
            points += 5
        if defect.get("workaround") == "false":
            points += 8

        items.append(
            RiskItem(
                category="open_defect",
                points=points,
                reason=f"{defect.get('id')} {severity} 미해결: {defect.get('title')}"
            )
        )
    return items


def score_failed_tests(test_results: list[dict[str, str]]) -> list[RiskItem]:
    items: list[RiskItem] = []
    for result in test_results:
        if result.get("status") != "failed":
            continue

        criticality = result.get("criticality", "low")
        points = CRITICAL_TEST_POINTS.get(criticality, 3)
        items.append(
            RiskItem(
                category="failed_test",
                points=points,
                reason=f"{result.get('id')} 실패: {result.get('case_name')} ({result.get('area')})"
            )
        )
    return items


def score_change_scope(release: dict) -> list[RiskItem]:
    items: list[RiskItem] = []
    for change in release.get("change_scope", []):
        criticality = change.get("criticality", "low")
        change_size = change.get("change_size", "small")
        points = AREA_POINTS.get(criticality, 2)
        if change_size == "large":
            points += 10
        elif change_size == "medium":
            points += 5

        items.append(
            RiskItem(
                category="change_scope",
                points=points,
                reason=f"{change.get('area')} 변경 범위: {criticality}/{change_size}"
            )
        )
    return items


def score_coverage(release: dict) -> list[RiskItem]:
    coverage = release.get("automation_coverage", {})
    overall = int(coverage.get("overall", 0))
    critical_flow = int(coverage.get("critical_flow", 0))
    items: list[RiskItem] = []

    if overall < 70:
        items.append(RiskItem("coverage", 10, f"전체 자동화 커버리지 낮음: {overall}%"))
    if critical_flow < 65:
        items.append(RiskItem("coverage", 15, f"핵심 플로우 자동화 커버리지 낮음: {critical_flow}%"))

    return items


def calculate_risk_score(release: dict, defects: list[dict[str, str]], test_results: list[dict[str, str]]) -> tuple[int, list[RiskItem]]:
    items = [
        *score_open_defects(defects),
        *score_failed_tests(test_results),
        *score_change_scope(release),
        *score_coverage(release)
    ]
    score = min(sum(item.points for item in items), 100)
    return score, sorted(items, key=lambda item: item.points, reverse=True)

