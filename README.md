# QA Release Gate - 릴리즈 리스크 판단 대시보드

> 테스트 결과, 미해결 결함, 변경 범위, 자동화 커버리지를 종합해 이번 릴리즈를 배포해도 되는지 판단하는 QA 의사결정 프로젝트입니다.
> 핵심은 테스트를 많이 돌리는 것이 아니라, 릴리즈 리스크를 설명 가능한 기준으로 판단하는 것입니다.

## 데이터 안내

이 저장소의 릴리즈 정보, 결함, 테스트 결과, 변경 범위는 모두 직접 만든 가상 샘플 데이터입니다. 현재 또는 과거 회사/고객사의 이슈, 운영 지표, 릴리즈 기록, 결함 데이터는 포함하지 않습니다.

## 이 프로젝트가 다루는 문제

릴리즈 직전 QA는 단순히 테스트 통과 여부만 보는 것이 아니라 여러 질문을 함께 판단해야 합니다.

- P1/P2 결함이 남아 있는가?
- 실패한 테스트가 핵심 사용자 흐름에 영향을 주는가?
- 변경 범위가 결제, 인증 같은 critical area에 집중되어 있는가?
- 자동화 커버리지가 낮은 영역은 수동 보강이 되었는가?
- 조건부 배포라면 모니터링과 rollback 기준이 준비되어 있는가?

이 저장소는 이런 판단을 `GO`, `CONDITIONAL_GO`, `NO_GO`로 구조화합니다.

## 판정 기준

| 판정 | 의미 |
| --- | --- |
| `GO` | 현재 기준에서 릴리즈 진행 가능 |
| `CONDITIONAL_GO` | 릴리즈는 가능하지만 조건부 승인, 보강 테스트, 강화 모니터링 필요 |
| `NO_GO` | 핵심 결함 또는 critical 테스트 실패로 릴리즈 보류 필요 |

## 리스크 모델

처음부터 복잡한 AI 판단을 쓰지 않고, 설명 가능한 rule-based 모델로 구성했습니다.

| 리스크 요소 | 예시 |
| --- | --- |
| 미해결 결함 | P1/P2 open defect, 고객 영향, workaround 여부, reopen 여부, 결함 age |
| 테스트 결과 | critical/high 실패, blocked 테스트, flaky warning, manual evidence |
| 변경 범위 | critical area 변경, 변경 크기, 외부 의존성, data migration 여부 |
| 자동화 커버리지 | 전체/핵심 플로우/변경 영역 커버리지 부족 |
| 품질 신호 | smoke/regression/API pass rate, flaky count, blocked count |
| 릴리즈 준비도 | QA sign-off, 운영 승인, rollback plan/test, 모니터링 owner 준비 |

예시 점수:

```text
risk_score =
  unresolved_p1 * 40
+ failed_critical_tests * 20
+ critical_area_change * 15
+ low_critical_flow_coverage * 15
```

점수는 100점으로 cap 처리하며, 점수뿐 아니라 어떤 항목이 위험을 높였는지 함께 출력합니다.

## 입력 데이터

현재 버전은 외부 시스템에 직접 연결하지 않고, 릴리즈 판단에 필요한 파일을 읽어 점수를 계산합니다.

| 파일 | 의미 |
| --- | --- |
| `data/release_sample.json` | 릴리즈 기본 정보, 변경 범위, 자동화 커버리지, 품질 신호, 승인/rollback 준비 상태 |
| `data/defects_sample.csv` | 미해결/해결 결함 목록, 심각도, 고객 영향, 우회 가능 여부, 결함 age, QA 검증 여부 |
| `data/test_results_sample.csv` | smoke/regression/API/visual 테스트 결과, criticality, failed/blocked/warning 상태, evidence |
| `data/change_scope_sample.json` | 변경 모듈, feature flag, 외부 의존성, 수동 QA focus note |

예를 들어 결함 데이터는 단순히 P1/P2 개수만 보지 않습니다.

```csv
id,title,severity,status,area,affected_flow,customer_impact,workaround,reopened,age_days,verified_by_qa,linked_test
BUG-101,Payment confirmation intermittently fails,P1,open,payment,checkout,high,false,true,4,false,TC-002
```

테스트 결과도 단순 pass/fail보다, 어떤 계층의 어떤 critical flow가 실패했는지 보도록 구성했습니다.

```csv
id,layer,suite,case_name,area,criticality,status,execution_type,evidence,flaky,failure_reason
TC-002,ui,smoke,checkout_card_payment,payment,critical,failed,automated,screenshot,false,confirmation timeout
```

이 구조는 나중에 Jira, GitHub Actions, Excel 체크리스트, CI 리포트에서 데이터를 가져오는 형태로 확장할 수 있습니다.

## 프로젝트 구조

```text
qa-release-gate/
- data/
  - release_sample.json
  - defects_sample.csv
  - test_results_sample.csv
  - change_scope_sample.json
- gate/
  - data_loader.py
  - risk_model.py
  - release_gate.py
  - report_generator.py
- dashboard/
  - streamlit_app.py
- tests/
  - test_risk_model.py
  - test_release_gate.py
- run_gate.py
```

## 빠른 실행

```bash
pip install -r requirements.txt
python run_gate.py
```

실행하면 `reports/release_gate_report.md`가 생성됩니다.

예상 출력:

```text
Release Gate: NO_GO
Risk Score: 100/100
Report: reports/release_gate_report.md
```

## 대시보드 실행

```bash
streamlit run dashboard/streamlit_app.py
```

대시보드에서는 다음 항목을 확인할 수 있습니다.

- 릴리즈 판정
- Risk Score
- 주요 리스크 Top 5
- 권장 QA 액션
- 릴리즈 변경 범위
- 미해결 결함
- 테스트 결과

## 테스트

```bash
pytest -q
```

테스트는 다음 판단 로직을 검증합니다.

- P1 미해결 결함이 있으면 `NO_GO`
- 중간 수준 리스크는 `CONDITIONAL_GO`
- 낮은 리스크는 `GO`
- 리스크 점수는 100점을 넘지 않음
- resolved defect는 리스크에 포함하지 않음

## QA 포트폴리오 관점

이 프로젝트는 자동화 스크립트보다 릴리즈 품질 판단에 초점을 둡니다.

시니어 QA 관점에서 중요한 것은 "테스트를 실행했다"가 아니라, "이 릴리즈가 나가도 되는지 어떤 근거로 판단했는가"입니다. 이 저장소는 그 판단 기준을 데이터, 규칙, 리포트, 대시보드로 분리해 보여줍니다.

## 확장 아이디어

- Jira 또는 GitHub Issues에서 결함 데이터 수집
- CI 테스트 결과 XML/JSON import
- 릴리즈별 리스크 추세 시각화
- LLM을 사용한 릴리즈 요약 초안 생성
- `aiops-sentinel`과 연결해 AI가 작성한 릴리즈 요약의 누락/과장 여부 평가

## GitHub About 추천 문구

```text
시니어 QA 관점의 릴리즈 리스크 판단 대시보드. 테스트 결과, 미해결 결함, 변경 범위, 자동화 커버리지를 종합해 GO / CONDITIONAL_GO / NO_GO를 산출합니다.
```

## 추천 Topics

```text
qa, release-gate, risk-based-testing, test-strategy, quality-engineering, python, streamlit
```
