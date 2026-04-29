# 삼온 케어 로봇 (Samon Care Robot)

> **Upstage × SeSAC AI 서비스 개발 (기획 → 구현) 프로젝트 — 기업 협업 과제 (LG전자)**
> NASA-JPL ROSA 5계층 아키텍처를 LG CLOi 플랫폼 위에 얹어 *가정 돌봄* 도메인으로 확장한 use case.
> *낮에는 인지중재, 밤에는 다약제 안전 모니터링.*

**Program**: Upstage × SeSAC AI 서비스 개발 프로젝트 (기획-구현 일괄 트랙)
**Corporate Partner / Mission Owner**: LG전자
**Domain Lead (본 문서 작성자)**: 황지은 (Jieun Hwang) — RN, MS in Integrative Medicine
**Built on**: [nasa-jpl/rosa](https://github.com/nasa-jpl/rosa) + LG CLOi 플랫폼 + Upstage Solar LLM
**Upstream contribution**: [nasa-jpl/rosa#82](https://github.com/nasa-jpl/rosa/pull/82)

---

## 0. 원본 미션과 본 프로젝트의 진화

LG전자 현직자가 제시한 원본 미션은 *"가구 자동화 공장의 로봇들이 자연재해로 메모리를 잃었다 — 각 로봇에 가상의 기억을 JSON으로 만들어 이식하라"* 였다. 본 팀은 5단계 워크플로우(기억 요소 요청 → 가상 기억 생성 → JSON 출력 → key-value 변환 → 3대 로봇 메모리 생성) 를 그대로 따르되, **임상 가치가 훨씬 큰 도메인** 으로 확장했다 — 가정 돌봄 로봇.

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
| **LG전자** | LG CLOi 서비스 로봇 (자율주행·HRI 검증), ThinQ Care 비전, 글로벌 가전 채널 | 하드웨어 플랫폼 + 상용화 채널 |
| **Upstage** | Solar LLM (한국어 최강, 의료 도메인 fine-tune 가능), Document AI | LLM 추론·메모리 RAG 백엔드 |
| **SeSAC** | 청년 인재 풀, 프로토타입 인프라 | 빌드 + 통합 |
| **Domain Expertise (본 팀)** | 임상 8년·공공보건 5년·VIP 1:1 간호 5년·통합의학 석사 | 가정 돌봄 시나리오 설계, 임상 가드레일, 콘텐츠 큐레이션 |

본 산출물은 *startup pitch*가 아니라 **LG CLOi 신제품 라인업의 가정 돌봄 트랙**으로 직접 진입 가능한 use case이다.

## 2. 무엇을 만들었는가

LG CLOi 하드웨어 위에 동작하는 **두 모드 단일 로봇**.

| 모드 | 시간대 | 작동 |
|------|--------|------|
| 인지중재 모드 | 주간 (10:00 ~ 18:00) | 한국무용·국악·세대별 회상 사진 기반 비약물 인지중재(CST) |
| 다약제(polypharmacy) 안전 모니터링 모드 | 야간 (18:00 ~ 22:00) | 5종 이상 동시 복용자 대상, 복약 후 30분 얼굴·음성·심박 모니터링, 부작용 자동 감지 |

*"삼온(三溫)"* 의 의미: **몸의 온기**(다약제 안전) + **마음의 온기**(인지중재) + **가족의 온기**(연결).
*프로젝트 코드네임이며, LG 상용화 시 별도 브랜드 적용 가능.*

## 3. 왜 지금인가 — 정책·기술·시장의 3박자 정렬

### 정책: 통합돌봄법 (2026.3.20 시행)
13조 원 예산. 재택의료센터 200곳 1차 → 2027년 600곳. 정책이 보상하는 건 *"병원 밖에서 의료-돌봄이 끊기지 않게"* 만드는 행위. **LG CLOi가 가정에 들어가는 첫 정책 윈도우**.

### 기술: ROSA + LG CLOi + Upstage Solar
- ROSA의 5계층 에이전틱 아키텍처(인식·계획·스킬·메모리·자기반성)는 본래 *터틀 좌표*를 위해 설계됐지만, 그대로 *환자 임상 데이터 + 로봇 센서·모터*로 매핑 가능
- LG CLOi가 hospitality·service 영역에서 검증한 자율주행·HRI 역량을 *가정 환경*으로 가져오는 첫 제품
- Upstage Solar는 한국어 의료 발화·환자 자가보고를 가장 정확히 처리할 수 있는 국내 LLM (데이터 주권·규제 친화)

### 시장: 고령사회 + 관절염·거동제한 환자가 가장 절실하다
- 65세+ **950만 명**, 그중 **관절염 유병률 50%(약 480만 명)** — 외출·이동이 가장 어려운 인구
- *"부엌까지 약 가지러 가는 5미터 거리가 통증으로 막힌다"* — 무릎·고관절 골관절염의 일상 페인포인트
- 거동 제한 → 외출 빈도 감소 → 인지 자극 부족 → 치매 가속 → 낙상 위험 ↑ — 하나의 환자에게 **다약제 + 인지저하 + 낙상**이 동시에 누적되는 구조
- 약물 부작용 응급실 방문 23만 건/년, 65세+ 낙상 50만 건/년
- TAM 5.7조 (65세+ × 월 5만 원), B2C + B2B(요양원·재택의료센터) + 글로벌(LG의 일본·동남아 채널)

### 삼온 케어 로봇이 관절염·거동제한 어르신께 정확히 맞는 이유
1. **약을 어르신께 가져간다** — 자율주행으로 약통을 거실 소파 옆까지. 부엌 5미터 이동이 사라짐
2. **모든 인터랙션이 음성** — 무릎 굽혀 폰 조작할 필요 없음, 손목 비틀어 워치 누를 필요 없음
3. **인지중재가 거실에서 이뤄진다** — 외출 못 해도 한국무용 영상·회상 대화로 정서·인지 자극 30분/일
4. **낙상은 LiDAR가 본다** — 손목 워치 안 차도, 휴대폰 안 들어도 4채널 fusion으로 감지 + 119 자동
5. **다약제 모니터링이 옆에서 따라간다** — 복용 후 30분간 어지러움·심박이상 자동 감지로 *낙상 전에* 가족 알림

## 4. ROSA 5-Layer → 삼온 케어 로봇 매핑

| Layer | ROSA 원형 (TurtleSim) | 삼온 적용 (LG CLOi 기반) |
|-------|------------------------|---------------------------|
| 1. Multi-modal Perception | 터틀 좌표·장애물 | LG CLOi 카메라 · 마이크 · LiDAR · 터치 + 외부 웨어러블 6채널 |
| 2. Goal-to-Plan | "별 그려줘" → 좌표 | Upstage Solar로 시간대+음성+상태 → 인지중재/다약제/응급 분기 |
| 3. Plan-to-Skill | move/turn API | LG CLOi 모터·디스플레이·스피커 + 알림 + 약물DB · EMR API |
| 4. Memory & Context | 이전 도형 기억 | 환자별 약물·가족·선호 음악·인지중재 패턴 장기보존 (Upstage RAG) |
| 5. Self-reflection | 실패 도형 압축 | 콘텐츠 효과 학습 · 알림 임계값 자동 조정 (RN/MD 검토 후 적용) |

자세한 설명: [docs/01-architecture-mapping.md](docs/01-architecture-mapping.md)

## 5. 글로벌 경쟁 환경 — 비어 있는 가정 돌봄 카테고리

| 솔루션 | 국가 | 위치 | 한계 |
|--------|------|------|------|
| Paro | 일본 | 정서 지원 물범 로봇 | 인지중재 효과 미입증 |
| ElliQ | 이스라엘/미국 | 음성 기반 노인 동반자 | 임상 모니터링 없음 |
| Buddy | 프랑스 | 가정 동반 로봇 | 의료 도메인 가드레일 없음 |
| Robear | 일본 | 의료기관용 이송 로봇 | 가정용 부적합 |
| **삼온 (LG CLOi 기반)** | **한국** | **임상 모니터링 + K-콘텐츠 인지중재** | — |

핵심 차별 한 줄: *해외 가정용 로봇은 정서 지원에 멈췄고, 국내 제품은 단순 알림에 멈췄다. 삼온은 임상-모니터링과 K-콘텐츠 인지중재를 결합한 첫 카테고리.*

## 6. 3-Phase 상용화 로드맵 (LG CLOi 라인업 정렬)

| Phase | 기간 | 핵심 산출물 | 트랙 |
|-------|------|-------------|------|
| **Phase 0** | 2026 Q3 (3개월) | **인지중재 모듈 단독 출시 + 다약제·응급 확장 협업 시작** | Upstage×SeSAC AI 서비스 개발 프로젝트 (기업 협업 과제) |
| **Phase 1** | 2026 Q4 ~ 2027 Q2 | **LG CLOi for Home Care 베타** | LG 사내 검증, SaMD Class 2 인증 |
| **Phase 2** | 2027 Q3 ~ | **통합돌봄 200곳 + 글로벌 출시** | LG 글로벌 채널 (일본·동남아·중동) |

## 7. 시나리오

| ID | Title | Demo 우선순위 |
|----|-------|----------------|
| A | 다약제 사후 모니터링 (저녁 약 7가지 복용 후 30분 임상 추적) | Primary |
| B | 한국무용 회상 인지중재 (오후 3시, 어머니의 결혼식 영상 회상) | Secondary |
| C | 통합 응급 (낙상 감지 → 자녀 영상 연결 → 119 자동 안내) | Tertiary |

상세: [docs/02](docs/02-scenario-a-polypharmacy.md), [docs/03](docs/03-scenario-b-cognitive-care.md), [docs/04](docs/04-scenario-c-emergency-bridge.md)

## 8. 규제·안전성

본 시스템은 **진단·처방을 일절 수행하지 않는다.** 의료법 27조, 식약처 SaMD 가이드라인, 개인정보보호법, 통합돌봄법을 설계 단계부터 내장. 자세한 검토: [docs/05](docs/05-regulatory-considerations.md)

## 9. License & Acknowledgements

- License: **Apache 2.0** — NASA-JPL ROSA와 동일
- Built on: [nasa-jpl/rosa](https://github.com/nasa-jpl/rosa) by Jet Propulsion Laboratory, NASA
- Hardware partner: **LG전자 CLOi**
- LLM partner: **Upstage Solar**
- Program: **Upstage × SeSAC AI 서비스 개발 프로젝트 — 기업 협업 과제 (LG전자) (2026)**
- Upstream PR: [nasa-jpl/rosa#82](https://github.com/nasa-jpl/rosa/pull/82)

## 10. Contact

- GitHub: [@hje2555-bot](https://github.com/hje2555-bot)
- Email: hje2555@gmail.com

---

*"임상 현장에서 보지 못한 것을, AI는 더더욱 보지 못한다. 도메인이 먼저, 모델은 그 다음이다.
하드웨어가 그 사이를 잇는다."*
