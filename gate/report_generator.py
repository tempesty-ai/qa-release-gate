from __future__ import annotations

from pathlib import Path

from gate.release_gate import GateResult


def render_markdown(result: GateResult, release: dict) -> str:
    risk_lines = "\n".join(
        f"- {risk.reason} (+{risk.points})"
        for risk in result.top_risks
    )
    action_lines = "\n".join(f"- {action}" for action in result.recommended_actions)

    return f"""# Release Gate Report

## 판정

| 항목 | 값 |
| --- | --- |
| Release | {release.get("release_id")} |
| Service | {release.get("service")} |
| Status | {result.status} |
| Risk Score | {result.score} / 100 |

{result.summary}

## 주요 리스크

{risk_lines}

## 권장 QA 액션

{action_lines}
"""


def write_report(result: GateResult, release: dict, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(result, release), encoding="utf-8")
    return path

