# 06. 메모리 생성 워크플로우 — 원본 미션에서 가정 돌봄까지

## 0. 출발점 — 메모리 복원 시나리오

본 과제의 출발점은 *자연재해로 메모리가 손실된 자동화 공장 로봇들에게, 각각 다른 가상의 기억을 JSON 형식으로 만들어 이식하는 시나리오* 였다 (개념적 학습 과제, 출처는 비공개).

**기술적 제약**: 모든 학습 자원(프로그래밍, 자료구조, RAG, WORKFLOW) 자유 활용. **로봇에 입력되는 메모리는 JSON 형식**.

**5단계 메모리 생성 워크플로우 (학습 단계에서 정의된 표준 도식)**:
1. 기억 요소 요청하기 (사람의 기억을 구성하는 요소를 AI로 탐색)
2. 기억 요소를 기반으로 가상 기억 생성
3. 가상 기억을 JSON으로 출력
4. *"기억요소:가상기억"* 을 key-value 형태로 출력 (JSON)
5. 총 3대의 로봇에 이식될 기억 만들기 (JSON 형식)

## 1. 본 프로젝트의 답 — 같은 워크플로우, 더 임팩트 있는 도메인

원본 미션은 *가구 공장 자동화 로봇*의 메모리 복원이었다. 본 과제 팀은 같은 *메모리 생성 워크플로우* 의 **임상 가치가 훨씬 큰 적용 도메인** 을 식별했다 — **가정 돌봄 로봇 (CLOi-class robotic platform 적용 가설, 삼온)**.

| 비교 항목 | 원본 미션 (가구 공장) | 본 프로젝트 (가정 돌봄) |
|----------|------------------------|---------------------------|
| 로봇 위치 | 공장 라인 | 어르신 가정 |
| 메모리 대상 | 작업 공정·도구 사용 이력 | 환자 이력·가족·선호·일상 패턴 |
| 메모리 손실 영향 | 생산 라인 정지 | 환자 안전·돌봄 연속성 위협 |
| 시장 임팩트 | B2B (공장 1곳) | B2C + B2B (어르신 950만) |
| 정책 정합성 | 산업안전법 | 통합돌봄법 (2026.3) |
| 데모 페르소나 | 로봇 3대 (작업 종류별) | 어르신 3명 (의료 프로필별) |

**핵심 통찰**: 두 도메인 모두 *"개체별 차별화된 가상 기억을 JSON 구조로 이식"* 이라는 동일한 기술 문제를 푼다. NASA-JPL ROSA의 5계층 중 **Layer 4 (Memory & Context)** 가 정확히 이 문제의 표준 해법.

## 2. 5단계 워크플로우 — 본 프로젝트 적용

### Step 1. 기억 요소 요청 (Memory Element Elicitation)

LLM(Upstage Solar 또는 Claude)에게 *"가정 돌봄 로봇이 한 어르신을 안전하게 돌보려면 어떤 기억 요소가 필요한가"* 질의.

추출된 7개 요소 카테고리:

| Category | 예시 |
|----------|------|
| Demographics | 이름, 나이, 성별, 거주 형태 |
| Medical History | 진단명, 처방약, 알레르기, 입원 이력, 통증 부위 |
| Family & Emergency | 가족 구성, 1·2차 보호자 연락처, ACP 사전돌봄계획 |
| Preferences | 선호 음악·콘텐츠·식습관·종교 |
| Daily Routine | 기상·취침·식사·복약·외래 일정 |
| Pain Points | 관절염 부위, 인지 약점, 외출 어려움 정도 |
| Emotional Triggers | 트라우마·반복 호소·감정 회피 주제 |

이는 ROSA Layer 4의 **Semantic Memory** (환자 특이 사실) 와 직접 매핑된다.

### Step 2. 기억 요소 → 가상 기억 생성 (Persona Generation)

각 요소를 자연스러운 1인칭 서사 형태로 LLM에게 생성 요청.

예시 prompt:
```
당신은 76세 한국인 여성 박순자의 자전적 기억을 1인칭으로 작성합니다.
- 1971년 결혼, 미용실 30년 운영, 2024년 남편 사별
- MCI(경도인지장애) MMSE 25점, 무릎 관절염
- 좋아하는 노래: 이미자 동백 아가씨
- 외출 어려움, 며느리·아들과 동거
3개의 episodic 기억(과거 사건), 5개의 semantic 사실, 2개의 procedural 패턴을 JSON으로 출력하세요.
```

### Step 3. JSON 출력

ROSA `memory_schema.py` 의 pydantic 모델을 사용해 타입 안전한 JSON 직렬화.

```json
{
  "patient_id": "park_sunja",
  "episodic_memories": [...],
  "semantic_facts": {...},
  "procedural_patterns": [...]
}
```

### Step 4. Key-Value 형식

원본 미션의 *"기억요소:가상기억"* 매핑을 그대로 구현. semantic_facts 가 정확히 이 구조다.

```json
{
  "demographics.name": "박순자",
  "demographics.age": 76,
  "medical.diagnosis": "MCI, knee osteoarthritis",
  "preferences.favorite_song": "동백 아가씨 (이미자, 1964)",
  "family.primary_caregiver": "며느리 (52세, 동거)",
  "routine.outdoor_difficulty": "관절염 통증으로 외출 빈도 월 1회 미만"
}
```

### Step 5. 3대 로봇에 이식될 메모리 (JSON)

원본 미션은 *가구 공장 로봇 3대*. 본 과제는 *어르신 3명을 돌볼 케어 로봇 3대* 의 메모리를 생성한다.

| Robot ID | Persona | 시나리오 | 파일 |
|----------|---------|----------|------|
| `samon_001` | 박순자 (76세, MCI + 관절염) | 한국무용 회상 인지중재 (Scenario B) | `examples/sample_memories/robot_1_park_sunja.json` |
| `samon_002` | 김영석 (78세, 다약제 7종) | 다약제 사후 모니터링 (Scenario A) | `examples/sample_memories/robot_2_kim_youngseok.json` |
| `samon_003` | 이정자 (78세, 관절염 + 다약제 + 응급 이력) | 통합 응급 (Scenario C) | `examples/sample_memories/robot_3_lee_jeongja.json` |

각 JSON은 동일한 스키마를 사용하지만 *완전히 다른 기억* 을 담는다. 이것이 원본 미션의 *"각각 다른 기억을 제작하여 이식"* 요구사항을 충족한다.

## 3. 워크플로우 실행 코드

`examples/memory_generation_workflow.py` 에 5단계가 함수 단위로 구현되어 있다. 실행:

```bash
PYTHONPATH=src python examples/memory_generation_workflow.py
```

출력:
- 콘솔: 5단계 진행 로그
- 파일: `examples/sample_memories/robot_{1,2,3}_*.json` 자동 생성
- 검증: 각 JSON이 `rosa_healthcare.memory_schema` pydantic 모델로 round-trip 가능

## 4. RAG 통합 (Layer 4 ↔ Step 1·2)

원본 미션의 *"RAG 자유 활용"* 제약을 따라, 메모리 생성 단계에서 RAG를 다음과 같이 활용한다.

- **외부 지식 소스**: 한국 노인 의료 가이드라인 (대한노인의학회), 인지중재 콘텐츠 DB (한국무용 영상·국악 곡목·세대별 사진)
- **검색 인덱스**: BM25 + dense embedding 하이브리드 (환자 ID + 시간 + 카테고리 3축)
- **생성 단계**: 페르소나 prompt에 RAG로 검색된 *문화적 맥락* (예: 1970년대 결혼식 풍습, 미용실 운영 시대상) 을 자동 주입해 자연스러움 향상

## 5. 발전 방향 — 가구 공장에서 가정으로

본 프로젝트는 출발점이 된 메모리 복원 시나리오를 다음과 같이 발전시켰다.

1. **도메인 확장**: 공장 자동화 → 가정 돌봄 (TAM 5.7조 시장 + 통합돌봄법 정책 정합)
2. **메모리 모델 정교화**: 단순 작업 이력 → ROSA 5계층 (Episodic + Semantic + Procedural + Self-reflection)
3. **윤리·규제 가드레일**: 산업안전법 → 의료법 27조 + 식약처 SaMD + 개인정보보호법
4. **콘텐츠 IP**: 작업 매뉴얼 → 한국무용·국악 K-콘텐츠 (글로벌 수출 자산)
5. **실증 트랙**: 단일 공장 → 가전 양산 + 글로벌 채널 (가설)

## 6. 다음 문서

- 메모리 스키마 코드: [src/rosa_healthcare/memory_schema.py](../src/rosa_healthcare/memory_schema.py)
- 워크플로우 실행 코드: [examples/memory_generation_workflow.py](../examples/memory_generation_workflow.py)
- 3대 로봇 샘플 JSON: [examples/sample_memories/](../examples/sample_memories/)
- 5계층 매핑: [01-architecture-mapping.md](01-architecture-mapp