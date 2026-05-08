from __future__ import annotations

from dataclasses import dataclass

from gate.risk_model import RiskItem, calculate_risk_score


@dataclass(frozen=True)
class GateResult:
    status: str
    score: int
    summary: str
    top_risks: list[RiskItem]
    recommended_actions: list[str]


def decide_gate(release: dict, defects: list[dict[str, str]], test_results: list[dict[str, str]]) -> GateResult:
    score, risks = calculate_risk_score(release, defects, test_results)
    open_p1 = [defect for defect in defects if defect.get("status") == "open" and defect.get("severity") == "P1"]
    failed_critical = [
        result for result in test_results
        if result.get("status") == "failed" and result.get("criticality") == "critical"
    ]

    if open_p1 or failed_critical or score >= 80:
        status = "NO_GO"
        summary = "핵심 결함 또는 critical 테스트 실패가 있어 릴리즈 보류가 필요합니다."
    elif score >= 45:
        status = "CONDITIONAL_GO"
        summary = "릴리즈는 가능하지만 조건부 승인과 강화된 모니터링이 필요합니다."
    else:
        status = "GO"
        summary = "현재 기준에서는 릴리즈 진행이 가능합니다."

    return GateResult(
        status=status,
        score=score,
        summary=summary,
        top_risks=risks[:5],
        recommended_actions=recommend_actions(status, risks)
    )


def recommend_actions(status: str, risks: list[RiskItem]) -> list[str]:
    actions = []
    categories = {risk.category for risk in risks}

    if "open_defect" in categories:
        actions.append("P1/P2 미해결 결함의 배포 영향과 우회 가능 여부를 재확인합니다.")
    if "failed_test" in categories:
        actions.append("실패한 smoke/regression 테스트를 수정 후 재실행합니다.")
    if "change_scope" in categories:
        actions.append("변경 범위가 큰 핵심 기능은 배포 후 집중 모니터링 대상으로 지정합니다.")
    if "coverage" in categories:
        actions.append("자동화 커버리지가 낮은 핵심 플로우는 수동 보강 테스트를 수행합니다.")
    if status == "NO_GO":
        actions.append("릴리즈 책임자와 결함 owner가 함께 보류 사유를 승인해야 합니다.")
    elif status == "CONDITIONAL_GO":
        actions.append("조건부 승인 항목과 rollback 기준을 릴리즈 노트에 명시합니다.")
    else:
        actions.append("배포 후 기본 smoke check와 모니터링을 진행합니다.")

    return actions

