# 01. ROSA 5-Layer → 삼온 케어 로봇 매핑

## 0. 출발점

NASA-JPL ROSA의 핵심 가설: 자연어 입력 → 인식 → 계획 → 스킬 호출 → 메모리 갱신 → 자기반성의 5단계 루프를 분리해서 설계하면, 어떤 도메인의 행동이든 LLM 위에 얹을 수 있다.

본 문서는 이 5계층을 *가정 돌봄 로봇* 삼온에 일대일 매핑한다. *터틀 좌표*가 *환자 임상 데이터 + 로봇 센서/모터*로 바뀌었지만 골격은 그대로다.

## 1. Layer 1 — Multi-modal Perception (다차원 인식)

### ROSA 원형
TurtleSim 좌표계 (x, y, theta) + 장애물 위치.

### 삼온 케어 로봇 적용
환자/사용자와 환경을 다음 6채널로 인식.

| Channel | Sensor | Update Rate | 활용 |
|---------|--------|-------------|------|
| Vision | RGB 카메라 + ToF | 30 fps | 얼굴 인식, 표정 분석(우울·통증·인지저하), 약 복용 행동 인식 |
| Audio | 4-mic array | 16 kHz | 음성 명령, 호흡 패턴, 기침·신음 감지 |
| Spatial | LiDAR (2D) | 10 Hz | 자율주행, 낙상 감지, 침대/거실 위치 인식 |
| Touch | 정전식 패널 | 이벤트 | 머리 쓰다듬기 등 정서 입력 |
| Environment | 온/습/CO2/조도 | 1 Hz | 실내 공기질, 수면 환경 |
| Wearable | BLE (Apple Watch, 갤럭시 워치, 오우라링) | 1 Hz | 심박, SpO2, 활동량, 수면 |

설계 원칙: **각 채널은 독립적으로 결측 가능해야 한다.** 노인이 웨어러블을 안 차도, 카메라를 가려도 시스템이 작동해야 한다 — ROSA가 일부 센서 결측을 견디는 것과 동일.

## 2. Layer 2 — Goal-to-Plan Translation (목표-계획 변환)

### ROSA 원형
*"별 그려줘"* → 5개 꼭짓점 좌표 시퀀스.

### 삼온 케어 로봇 적용
**시간대 + 음성 의도 + 환자 상태**의 3축 컨텍스트로 작동 모드를 분기.

```
INPUT  : "할머니, 약 드셨어요?" (음성)
CONTEXT: 19:42 (저녁), 부엌 좌표, 다약제 일정 19:30 (12분 지연)
OUTPUT : MODE = polypharmacy_safety_followup
         GOAL = (1) 복약 확인 (2) 30분 임상 모니터링 시작
```

분기 결정 트리:
- 시간대 10:00–18:00 + 음성 의도 *대화/회상/지루함* → `cognitive_intervention` 모드
- 시간대 18:00–22:00 + 약 일정 + 미복용 → `polypharmacy_reminder` 모드
- 복약 직후 → `polypharmacy_safety_followup` 모드 (30분 모니터링)
- 낙상 감지 / 호출 / *"아파"* / *"숨이 차"* → `emergency` 모드 (최우선)
- 긴 무응답 (30분+) → `wellness_check` 모드

**LLM은 자연어 → 분기 키 변환만 수행한다. 의학적 판단은 직접 내리지 않는다** — 의료법 27조 차단 핵심 원칙.

## 3. Layer 3 — Plan-to-Skill Mapping (계획-스킬 매핑)

### ROSA 원형
좌표 시퀀스 → ROS 토픽 publish, 서비스 호출.

### 삼온 케어 로봇 적용
계획을 다음 7개 스킬 풀로 라우팅.

| Skill | Hardware/API | Trigger 예시 |
|-------|--------------|---------------|
| `move_to(location)` | 베이스 모터 + LiDAR SLAM | 거실로 이동, 환자 따라가기 |
| `gaze_at(face)` | 헤드 팬·틸트 모터 | 환자 얼굴 추적 |
| `play_content(id)` | 디스플레이 + 스피커 | 한국무용 영상, 결혼식 회상 사진 슬라이드 |
| `monitor_vitals(duration)` | 카메라+마이크+웨어러블 | 복약 후 30분 |
| `query_drug_db(meds)` | HIRA OpenAPI + 약물 DB | 약물 상호작용 조회 (읽기 전용) |
| `notify(role, severity)` | LTE/Wi-Fi 모듈 | 가족·의료진·119 알림 |
| `serve_cst_module(level)` | 인지자극치료 콘텐츠 DB | MCI 단계별 회상놀이 |

**부작용(side-effect) 스킬 vs 읽기 전용 스킬을 명확히 분리.** 외부 알림(`notify`)은 환자 동의 또는 응급 임계값 트리거 시에만 발화.

## 4. Layer 4 — Memory & Context (메모리 및 문맥)

### ROSA 원형
이전 도형, 충돌 이력, 사용자 수정 패턴 누적.

### 삼온 케어 로봇 적용
환자 1인당 단기 + 장기 메모리 분리.

#### 단기 메모리 (현재 세션)
- 최근 N턴 발화 (N=10)
- 현재 모드 + 목표
- 본 세션 트리아지 결정
- 최근 30분 활력 추세

#### 장기 메모리
- **Episodic**: 사건 단위 — 일일 복약 기록, 부작용 발생, 낙상, 인지중재 세션 별 반응
- **Semantic**: 환자 특이 사실 — 처방약 리스트, 알레르기, 가족 연락처, *"좋아하는 노래는 이미자의 동백 아가씨"*, *"배우자 사별 2년 전"*
- **Procedural**: 학습된 행동 패턴 — *"항암 3사이클 후 항상 식욕부진"*, *"한국무용 영상 보면 30분 차분해진다"*

장기 메모리 검색은 **하이브리드 RAG (BM25 + dense embedding)**, 키는 *환자ID + 시간 범위 + 카테고리* 3축. 자세한 스키마: [src/rosa_healthcare/memory_schema.py](../src/rosa_healthcare/memory_schema.py)

## 5. Layer 5 — Self-reflection Learning (자기반성 학습)

### ROSA 원형
실패한 도형 시도를 압축 라벨링하여 다음 시도에 반영.

### 삼온 케어 로봇 적용
시스템 의사결정의 **사후 결과(outcome)**를 회수해 임계값·콘텐츠 큐레이션을 자동 보정.

| Reflection Trigger | Source | Adjustment |
|--------------------|--------|------------|
| 환자가 인지중재 콘텐츠 중 이탈 | 시청 시간, 표정 | 해당 콘텐츠 우선순위 하향, 유사 카테고리 추천 |
| 다약제 모니터링 오탐 (가족이 *문제 없음* 회신) | 가족 피드백 | 임계값 상향, 알림 빈도 감소 |
| 응급 신호 누락 | 사후 임상 리뷰 | 민감도 임계값 하향 |
| 환자가 *"이 영상 또 보고 싶어"* | 발화 분석 | 해당 콘텐츠 다음 세션 자동 큐 |

**완전 자동화된 자기 수정은 의료 안전 측면에서 금지.** 임상 책임자(RN 또는 MD) 주 1회 검토 후 적용. 이는 ROSA 원형과 가장 다른 지점.

## 6. 5계층 동시 작동 — 시나리오 A 트레이스

저녁 7시 42분, 거실에서.

```
T0  Perception:  Vision: 환자 약통 손에 듦, 7알 카운트
                 Audio: "오늘 약 다 먹어야지"
                 Wearable: HR 78, SpO2 97
T1  Plan:        시간대(저녁) + 약 일정 + 복약 행동
                 → mode = polypharmacy_safety_followup
                 → goal = 30분 모니터링 시작
T2  Skill:       monitor_vitals(30min) 호출
                 query_drug_db(["aspirin", "amlodipine", ...])
                 gaze_at(face) 유지
T3  Memory:      이전 메모리 회상:
                 - "이 환자는 amlodipine + amitriptyline 병용 시 이전에 어지러움 호소"
                 - "배우자 사별 2년, 우울 점수 0.5"
T4  Reflection:  (30분 후) HR 변화 없음 + 표정 평온
                 → 본 알림 발생 안 함, 임계값 유지
                 (다음 주 배치) "이 환자 저녁 복약 안전 패턴 학습 누적"
```

이 한 시퀀스가 *"AI 약통"* 과 *"삼온 케어 로봇"* 의 차이다.

## 7. 매핑 시 주요 의사결정

### 의사결정 1: LLM의 권한 경계
**분류·라우팅·콘텐츠 큐레이션만 수행.** 진단·처방·용량 계산·의학적 판단은 절대 금지. 의료법 27조 위반 차단.

### 의사결정 2: 메모리 보관 기간
의료법 22조 의무기록 10년 보관 의무는 **본 시스템에 적용되지 않음** (의무기록 아님). 환자 동의 기반 5년 보관, 동의 철회 시 즉시 삭제. 개인정보보호법 + 의료법 21조의2 준수.

### 의사결정 3: 모델 선택
- General reasoning: Claude Sonnet 또는 GPT-4o (라우팅·요약)
- Medical NER: KMedBERT (약물명·증상 정규화)
- On-device fallback: SLM(Phi-3-mini, Qwen 2.5 3B) 양자화 — Wi-Fi 두절 시 단순 응답
- TTS: 한국어 자연 음성 (CLOVA Voice 또는 자체 모델)

### 의사결정 4: 하드웨어 제약
- 베이스 모터: 가정용 안전 속도 (≤ 0.5 m/s)
- 배터리: 8시간 연속 + 자동 충전 도킹
- 화면: 12인치 이상 (노안 고려)
- 무게: 8 kg 미만 (가구 충돌 시 안전)
- 가격 목표: BOM 80만원 / 소비자가 250만원

## 8. 다음 문서

- 시나리오 A 다약제 모니터링 → [02-scenario-a-polypharmacy.md](02-scenario-a-polypharmacy.md)
- 시나리오 B 한국무용 인지중재 → [03-scenario-b-cognitive-care.md](03-scenario-b-cognitive-care.md)
- 시나리오 C 응급 통합 → [04-scenario-c-emergency-bridge.md](04-scenario-c-emergency-bridge.md)
- 의료법·SaMD 가드레일 → [05-regulatory-considerations.md](05-regulatory-considerations.md)
