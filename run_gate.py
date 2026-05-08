from __future__ import annotations

from pathlib import Path

from gate.data_loader import load_csv, load_json
from gate.release_gate import decide_gate
from gate.report_generator import write_report


ROOT = Path(__file__).resolve().parent


def main() -> None:
    release = load_json(ROOT / "data" / "release_sample.json")
    defects = load_csv(ROOT / "data" / "defects_sample.csv")
    test_results = load_csv(ROOT / "data" / "test_results_sample.csv")

    result = decide_gate(release, defects, test_results)
    output_path = write_report(result, release, ROOT / "reports" / "release_gate_report.md")

    print(f"Release Gate: {result.status}")
    print(f"Risk Score: {result.score}/100")
    print(f"Report: {output_path}")


if __name__ == "__main__":
    main()

