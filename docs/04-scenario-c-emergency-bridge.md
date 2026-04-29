# Scenario C — 응급 통합 (낙상·실신 → 가족 → 119)

> **Status**: Tertiary (Demo 마지막 30초 분량)
> **Source**: 응급실 8년 경력의 골든타임 운영 노하우
> **Regulatory target**: SaMD Class 2 (Phase 1과 묶음)

## 1. 왜 이 시나리오가 중요한가

한국 65세 이상 낙상 연 50만 건. 낙상 후 *발견 지연 1시간 초과*면 사망률 ×4. 통합돌봄법의 핵심 메시지 *"병원 밖에서도 의료-돌봄이 끊기지 않게"* 가 가장 강력하게 적용되는 순간이 바로 응급 상황이다.

기존 시장:
- 응급호출 버튼 (보건소 무료 배포): 환자가 의식 있고 누를 수 있어야 작동
- 효돌이 / 단순 IoT: 낙상 감지 정확도 낮음 (false positive 다수)
- 스마트워치 낙상 감지: 손목 분리·미착용 시 미작동

삼온의 강점: **카메라 + LiDAR + 마이크 + 웨어러블의 4채널 fusion 으로 낙상·실신·심정지를 다중 검증**, 그리고 **응급 알림에 환자 약물 정보 자동 첨부** — 응급실 의료진의 의사결정 시간 단축.

## 2. End-to-End Flow (3가지 분기)

### 2.1 Trigger
오전 6시 14분, 화장실 가는 길에 거실 카펫에 걸려 낙상. 환자 의식 있음.

### 2.2 Layer-by-layer

**Layer 1 (Perception)**
- LiDAR: 환자 높이 0.4m로 급격 하강 (정상 1.5m)
- Audio: *"아이고"* + 충격음
- Vision: 환자 바닥에 누운 자세 인식
- Wearable: HR 92 (+급상승), SpO2 95

**Layer 2 (Plan)**
- 멀티채널 신호 fusion → confidence 0.94 → 모드 `emergency_fall_detected`
- 의식 평가 분기:
  - 음성 응답 가능 + 자력 일어서기 시도 → `family_notify`
  - 음성 응답 가능 + 일어서기 못 함 → `family_call_first` + `medic_assess`
  - 음성 무응답 5초 → `119_immediate`

**Layer 3 (Skill)**
```
robot.move_to_safe_distance(patient, 1.5m)  # 깔리지 않게
robot.gaze_at(patient.face)
robot.say("정자님, 다치셨어요? 머리는 괜찮으세요? 일어나실 수 있으세요?")

if patient.responsive and patient.can_get_up:
    notify(role="family", severity="moderate",
           reason="낙상, 의식 있음, 자력 회복 시도",
           location="거실", time="06:14")
elif patient.responsive and not patient.can_get_up:
    notify(role="family", severity="high")
    video_call("son.kim")
    advise_position(patient, "옆으로 누워주세요")
else:  # 무응답
    notify(role="119", severity="critical",
           location="거실", incident="fall_unconscious",
           medications=patient.current_meds,
           recent_events=last_24h_summary)
    notify(role="family", severity="critical")
```

**Layer 4 (Memory)**
응급 시 자동 첨부 정보:
- 처방약 7종 리스트 (디곡신·와파린 등 응급실 의료진이 즉시 알아야 할 약물)
- 최근 24시간 활력 추세 + 복약 이력
- 알레르기·과거 입원 이력
- 가족 연락처 우선순위 + 환자 본인 ACP(사전돌봄계획) 문서

이 정보가 119 출동 동안 *응급실 EMR에 사전 도착* 하는 순간, 응급의료진의 trauma assessment 시간이 평균 8분 단축된다 (응급실 임상 데이터 기반 추정).

**Layer 5 (Reflection — async)**
사후 검토:
- 낙상 감지 정확도 (사후 가족 확인 결과와 비교)
- 119 출동 시간 + 응급실 도착 시간 + 처치 결과
- 본 환자의 낙상 위험인자 패턴 누적 → 미래 예방 알림 (예: *"새벽 화장실 동선에 야간 조명 + 카펫 제거 권유"*)

### 2.3 분기별 응답 예시

**분기 1 — 의식 있음 + 자력 회복 가능**
> *"정자님, 천천히 일어나세요. 머리·허리 안 아프시죠? 제가 며느님께 *지금 일어나셨다* 한 통화 드릴게요. 30분 동안 옆에 있을게요."*

**분기 2 — 의식 있음 + 자력 회복 불가**
> *"정자님, 무리해서 일어나지 마세요. 옆으로 천천히 누워주세요. 아드님 지금 영상통화 연결할게요. 119도 같이 부를게요. 괜찮으시죠?"*

**분기 3 — 무응답 5초**
> (자체 응답 중단, 즉시 119 자동 호출)
> 119 통신: *"삼온 케어 로봇 자동 신고. 76세 여성 박순자, 거실 낙상 후 의식 무응답. 처방약 7종 — amlodipine, furosemide, spironolactone, digoxin, amitriptyline, tramadol, zolpidem. 최근 활력 데이터 전송 중. 주소 [GPS]."*

이 한 통화가 응급실 도착 후 첫 처치까지 시간을 줄인다.

## 3. Demo plan

PoC 데모에서는 **분기 2를 30초 분량으로 시연**. 분기 3은 영상 자료로 1컷 보여주고 패스.

| Step | 시각화 |
|------|--------|
| 1 | LiDAR 그래프에서 환자 높이 급강하 |
| 2 | 4채널 fusion confidence 0.94 표시 |
| 3 | 메모리에서 처방약·가족 연락처 호출 |
| 4 | 가족 영상통화 + 119 알림 시뮬레이션 |
| 5 | 응급실 EMR에 정보 사전 전송 시각화 |

## 4. KPI

- 낙상 감지 sensitivity 0.95+, specificity 0.85+
- 응급 알림 평균 발화 시간 ≤ 8초 (트리거 → 가족 알림)
- 119 자동 호출 → 응급실 도착 시간 평균 단축 ≥ 5분
- 응급실 도착 시 약물 정보 인지 비율 90%+ (vs 기존 30%)

## 5. Business & Social Value

이 기능 하나만으로 *"왜 250만 원짜리 로봇을 사야 하는가"* 의 답이 된다. 가족 입장에서 *"부모님 새벽 낙상을 1시간 늦게 발견할 수 있다"* 는 공포가 핵심 구매 동인.

- B2C 보호자 결제 동기 70%+
- 보험 가산수가 가능성 — 응급의료 효율화 측면
- 사회적 가치: 독거노인 50만 명의 *고독사 예방* 정책과 직접 부합

## 6. 안전성·법적 가드레일

- **자체 의학적 처치 일절 금지** — *"움직이지 마세요"* 같은 자세 권유는 응급의학 표준 가이드 한정
- **119 자동 호출은 환자 사전 동의 + 가족 보호자 동의 ACP 문서 기반**
- **무응답 5초 임계값**은 false positive 최소화를 위한 conservative 값. 사후 reflection으로 점진 조정.
- **과거 응급 호출 기록은 의료진/가족 외 절대 비공개** — 개인정보보호법 + 보험 차별 방지
