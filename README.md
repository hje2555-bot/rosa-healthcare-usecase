# 삼온 케어 로봇 (Samon Care Robot) — Healthcare Domain Exploration

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Built on NASA-JPL ROSA](https://img.shields.io/badge/Built%20on-NASA--JPL%20ROSA-orange.svg)](https://github.com/nasa-jpl/rosa)
[![Status: Concept Exploration](https://img.shields.io/badge/Status-Concept%20Exploration-yellow.svg)](#-disclaimer-먼저-읽어주세요)
[![ROSA 5-Layer Mapped](https://img.shields.io/badge/ROSA-5--Layer%20Mapped-purple.svg)](docs/01-architecture-mapping.md)
[![Memory Workflow](https://img.shields.io/badge/Workflow-5--Step%20Memory%20Generation-green.svg)](docs/06-memory-generation-workflow.md)
[![Domain](https://img.shields.io/badge/Domain-Elderly%20Home%20Care-red.svg)](docs/00-executive-summary.md)
[![Upstream PR](https://img.shields.io/badge/Upstream%20PR-nasa--jpl%2Frosa%2382-lightgrey.svg)](https://github.com/nasa-jpl/rosa/pull/82)

> *Personal domain-extension exploration. Concept proposal, not an official deliverable.*

> NASA-JPL ROSA의 5계층 아키텍처를 가정 돌봄 도메인에 적용한 **개념 단계의 use case 탐구**.
> *낮에는 인지중재, 밤에는 다약제 안전 모니터링.*

## ⚠ Disclaimer (먼저 읽어주세요)

본 리포지토리는 *Upstage × SeSAC AI 서비스 개발 프로그램* 수강 중 **Domain Lead(작성자)가 개인적으로 진행한 healthcare 도메인 확장 탐구**입니다. 다음을 명확히 해 둡니다.

- **공식 산출물 아님**: 프로그램·기업 협업 과제의 공식 결과물이 아닙니다. 팀 메인 작업과는 별개의 개인 학습 트랙입니다.
- **어떤 회사도 본 내용을 승인·후원하지 않음**: 본문에 등장하는 회사·플랫폼·LLM 명칭은 *기술적 호환 가능성*을 가정한 개념 시나리오일 뿐, 해당 회사의 사업 계획·로드맵·제휴를 의미하지 않습니다.
- **로드맵·시장 규모 수치는 가설**: 모든 Phase 0/1/2 시점, 매출 시나리오, 글로벌 채널 언급은 *상용화될 경우의 가설적 경로*이며 실제 비즈니스 약속이 아닙니다.
- **임상 안전 청구 아님**: 본 시스템은 진단·처방·치료를 수행하지 않습니다. 의료기기 인증·임상 검증을 거치지 않은 개념 코드입니다.
- **권리 귀속**: 본인의 healthcare 도메인 적용 부분에 한정한 개인 산출물. 프로그램 운영 측이 별도 가이드 제시 시 해당 가이드를 우선합니다.

**Author**: 황지은 (Jieun Hwang) — RN, MS in Integrative Medicine
**Built on**: [nasa-jpl/rosa](https://github.com/nasa-jpl/rosa) (Apache 2.0)
**Upstream contribution**: [nasa-jpl/rosa#82](https://github.com/nasa-jpl/rosa/pull/82)

---

## 0. 원본 미션과 본 프로젝트의 진화

본 과제의 출발점은 *"메모리가 손실된 자동화 공장 로봇에 가상 기억을 JSON 형식으로 이식하는 시나리오"* 였다. 같은 5단계 메모리 생성 워크플로우(기억 요소 요청 → 가상 기억 생성 → JSON 출력 → key-value 변환 → N대 로봇 메모리 생성) 를 **임상 가치가 큰 가정 돌봄 도메인** 에 적용한 것이 본 healthcare 확장 탐구이다.

| 비교 | 원본 미션 (가구 공장) | 본 프로젝트 (가정 돌봄) |
|------|------------------------|---------------------------|
| 로봇 위치 | 공장 라인 | 어르신 가정 |
| 메모리 손실 영향 | 생산 라인 정지 | 환자 안전·돌봄 연속성 위협 |
| 시장 임팩트 | B2B 단일 공장 | B2C + B2B (어르신 950만) |
| 정책 정합 | 산업안전법 | 통합돌봄법 (2026.3) |
| 데모 | 로봇 3대 (작업별) | 어르신 3명 (의료 프로필별) |

자세한 설명: [docs/06-memory-generation-workflow.md](docs/06-memory-generation-workflow.md)
실행 가능한 코드 + 3개 JSON: [examples/memory_generation_workflow.py](examples/memory_generation_workflow.py), [examples/sample_memories/](examples/sample_memories/)

## 1. 본 프로젝트의 위치 — 세 파트너의 자산이 만나는 지점

| Partner | 보유 자산 | 본 프로젝트가 활용하는 영역 |
|---------|-----------|------------------------------|
| *하드웨어 참조 플랫폼* | CLOi급 서비스 로봇 (자율주행·HRI 검증된 service robot 플랫폼) | 하드웨어 호환 가능성 가정 (실제 채택 약속 없음) |
| **Upstage** | Solar LLM (한국어 최강, 의료 도메인 fine-tune 가능), Document AI | LLM 추론·메모리 RAG 백엔드 |
| **SeSAC** | 청년 인재 풀, 프로토타입 인프라 | 빌드 + 통합 |
| **Domain Expertise (본 팀)** | 임상 8년·공공보건 5년·프리미엄 회원제 1:1 전담간호 5년·통합의학 석사 | 가정 돌봄 시나리오 설계, 임상 가드레일, 콘텐츠 큐레이션 |

본 산출물은 *startup pitch*가 아니라 **CLOi급 서비스 로봇 플랫폼의 가정 돌봄 시나리오 (가설)**으로 직접 진입 가능한 use case이다.

## 2. 무엇을 만들었는가

CLOi급 서비스 로봇 플랫폼에서 동작 가능한 **두 모드 단일 로봇**.

| 모드 | 시간대 | 작동 |
|------|--------|------|
| 인지중재 모드 | 주간 (10:00 ~ 18:00) | 한국무용·국악·세대별 회상 사진 기반 비약물 인지중재(CST) |
| 다약제(polypharmacy) 안전 모니터링 모드 | 야간 (18:00 ~ 22:00) | 5종 이상 동시 복용자 대상, 복약 후 30분 얼굴·음성·심박 모니터링, 부작용 자동 감지 |

*"삼온(三溫)"* 의 의미: **몸의 온기**(다약제 안전) + **마음의 온기**(인지중재) + **가족의 온기**(연결).
*프로젝트 코드네임이며, 하드웨어 파트너 상용화 시 별도 브랜드 적용 전제.*

## 3. 왜 지금인가 — 정책·기술·시장의 3박자 정렬

### 정책: 통합돌봄법 (2026.3.20 시행)
13조 원 예산. 재택의료센터 200곳 1차 → 2027년 600곳. 정책이 보상하는 건 *"병원 밖에서 의료-돌봄이 끊기지 않게"* 만드는 행위. **가정용 서비스 로봇이 진입할 정책 윈도우**.

### 기술: ROSA + CLOi-class service robot platform + Upstage Solar
- ROSA의 5계층 에이전틱 아키텍처(인식·계획·스킬·메모리·자기반성)는 본래 *터틀 좌표*를 위해 설계됐지만, 그대로 *환자 임상 데이터 + 로봇 센서·모터*로 매핑 가능
- CLOi급 서비스 로봇이 hospitality·service 영역에서 검증한 자율주행·HRI 역량을 *가정 환경*으로 확장하는 가설적 적용
- Upstage Solar는 한국어 의료 발화·환자 자가보고를 가장 정확히 처리할 수 있는 국내 LLM (데이터 주권·규제 친화)

### 시장: 고령사회 + 관절염·거동제한 환자가 가장 절실하다
- 65세+ **950만 명**, 그중 **관절염 유병률 50%(약 480만 명)** — 외출·이동이 가장 어려운 인구
- *"부엌까지 약 가지러 가는 5미터 거리가 통증으로 막힌다"* — 무릎·고관절 골관절염의 일상 페인포인트
- 거동 제한 → 외출 빈도 감소 → 인지 자극 부족 → 치매 가속 → 낙상 위험 ↑ — 하나의 환자에게 **다약제 + 인지저하 + 낙상**이 동시에 누적되는 구조
- 약물 부작용 응급실 방문 23만 건/년, 65세+ 낙상 50만 건/년
- TAM 5.7조 (65세+ × 월 5만 원), B2C + B2B(요양원·재택의료센터) + 글로벌(글로벌 가전 유통 채널 (가설))

### 삼온 케어 로봇이 관절염·거동제한 어르신께 정확히 맞는 이유
1. **약을 어르신께 가져간다** — 자율주행으로 약통을 거실 소파 옆까지. 부엌 5미터 이동이 사라짐
2. **모든 인터랙션이 음성** — 무릎 굽혀 폰 조�