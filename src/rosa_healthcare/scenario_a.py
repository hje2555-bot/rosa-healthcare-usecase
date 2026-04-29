"""삼온 케어 로봇 — 시나리오 A 의사코드 (Polypharmacy Safety Followup).

대상 환자: 관절염·거동제한 + 다약제(polypharmacy, 5종 이상 동시 복용) 어르신.
   *부엌까지 5미터 이동이 무릎 통증으로 막히는 일상* 을 전제로 설계됐다.
   로봇이 어르신께 다가가는 방향으로 모든 모션이 짜여 있다.

ROSA 5계층의 흐름을 그대로 따라가는 의사코드.
실제 LLM·하드웨어 호출은 mock으로 처리되며, PoC 데모 + 코드 리뷰가 목적.

흐름:
    Layer 1 (Perception)   환자 약 복용 행동 감지 (거실에서, 어르신 이동 없이)
    Layer 2 (Plan)         시간대 + 행동 + 메모리 → polypharmacy_safety_followup 모드
    Layer 3 (Skill)        모터·디스플레이·모니터링 호출 (로봇이 환자에게 이동)
    Layer 4 (Memory)       과거 부작용 패턴 + 관절염 통증·낙상 이력 회상
    Layer 5 (Reflection)   30분 후 결과를 회수해 임계값 보정 (별도 비동기 배치)

의료법 27조 가드레일:
    - 본 코드는 진단·약품명·용량 발화를 절대 수행하지 않는다.
    - 약물 데이터베이스 조회는 read-only이며 출력은 트리아지/라우팅에만 사용된다.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from rosa_healthcare.memory_schema import (
    EpisodicMemory,
    PatientContext,
    RobotMode,
    Severity,
    SignalSource,
    SymptomCategory,
    TriageDecision,
    Utterance,
)

logger = logging.getLogger("samon.scenario_a")


# ───────────────────────────────────────────────
# Mock LLM / Hardware / External APIs
# ───────────────────────────────────────────────

class MockLLM:
    """실제로는 Claude Sonnet 또는 GPT-4o 호출.

    LLM의 권한 경계: 분류·라우팅·콘텐츠 큐레이션만 수행.
    진단·처방·용량 계산은 절대 금지 (의료법 27조).
    """
    def classify_intent(self, utterance: str, context: dict) -> str:
        # 실제: 자연어 → ["medication_intent", "small_talk", "complaint", ...]
        return "medication_intent"

    def filter_response(self, draft: str) -> str:
        """의료법 27조 위반 단어 자동 차단."""
        forbidden_patterns = [
            r"\b\d+\s*(mg|mcg|ml|정|알)\b",   # 용량
            r"(고혈압|당뇨병|심부전|우울증|불안장애)",  # 진단명 직접 발화
        ]
        # 실제: 정규식 + 의학 NER 모델
        return draft  # mock — 통과로 가정


class RobotHardware:
    """실제로는 ROS2 + 모터·LiDAR·카메라 드라이버."""
    def move_to(self, location: str) -> None:
        logger.info(f"[Hardware] move_to: {location}")

    def gaze_at(self, target: str) -> None:
        logger.info(f"[Hardware] gaze_at: {target}")

    def say(self, text: str) -> None:
        logger.info(f"[Hardware] TTS: {text}")

    def start_vitals_monitor(self, duration_min: int, signals: list[str]) -> "VitalsMonitor":
        logger.info(f"[Hardware] monitor start: {duration_min}min, signals={signals}")
        return VitalsMonitor()


@dataclass
class VitalsReading:
    timestamp: datetime
    hr: int                      # 분당 심박수
    spo2: int                    # 산소포화도 %
    facial_pallor: float         # 0.0~1.0 (창백)
    speech_slur: float           # 0.0~1.0 (언어 어눌함)
    balance_loss: float          # 0.0~1.0 (자세 불안)


class VitalsMonitor:
    """30분 모니터링 — 실제로는 카메라+마이크+웨어러블 fusion."""
    def stream(self) -> list[VitalsReading]:
        # mock — 정상 케이스
        now = datetime.now(timezone.utc)
        return [
            VitalsReading(now, 78, 97, 0.05, 0.02, 0.03),
        ]


class DrugDatabase:
    """HIRA OpenAPI 기반 약물 정보 (read-only)."""
    def check_interactions(self, meds: list[str]) -> list[dict]:
        # 실제: HIRA API 호출 + 약물 상호작용 DB
        # 출력 예시: [{"pair": ("amlodipine", "amitriptyline"),
        #              "risk": "orthostatic_hypotension", "severity": "moderate"}]
        return []


class NotificationService:
    def notify(self, role: str, severity: str, payload: dict) -> None:
        logger.info(f"[Notify] role={role}, severity={severity}, payload={payload}")


# ───────────────────────────────────────────────
# Layer 1 — Perception
# ───────────────────────────────────────────────

@dataclass
class PerceptionFrame:
    """다채널 센서 융합 결과 한 프레임."""
    timestamp: datetime
    medication_action_detected: bool      # vision: 약 복용 손동작
    pill_count: Optional[int]             # vision: 약 알 카운트
    utterance_text: Optional[str]         # audio: ASR 결과
    location: str                          # spatial: 부엌, 거실, 침실
    wearable_hr: Optional[int]
    wearable_spo2: Optional[int]


def perceive(sensors: dict[str, Any]) -> PerceptionFrame:
    """6채널 센서 데이터 → 통합 프레임.

    각 채널은 독립적으로 결측 가능 (None 허용).
    sensors["timestamp"]가 있으면 그 시각을 사용하고, 없으면 현재 시각.
    """
    return PerceptionFrame(
        timestamp=sensors.get("timestamp") or datetime.now(timezone.utc).astimezone(),
        medication_action_detected=sensors.get("vision_med_action", False),
        pill_count=sensors.get("vision_pill_count"),
        utterance_text=sensors.get("audio_asr"),
        location=sensors.get("spatial_location", "unknown"),
        wearable_hr=sensors.get("wearable_hr"),
        wearable_spo2=sensors.get("wearable_spo2"),
    )


# ───────────────────────────────────────────────
# Layer 2 — Goal-to-Plan Translation
# ───────────────────────────────────────────────

def plan(frame: PerceptionFrame, ctx: PatientContext, llm: MockLLM) -> RobotMode:
    """시간대 + 음성 의도 + 환자 상태 + 메모리 → 모드 결정.

    LLM은 자연어 → 의도 분류만 수행한다. 의학적 판단을 직접 내리지 않는다.
    """
    hour = frame.timestamp.astimezone().hour

    # 응급 신호 — 최우선
    if (frame.utterance_text and any(
        kw in frame.utterance_text for kw in ["아파", "숨이 차", "어지러워"])):
        if frame.utterance_text and "어지러워" in frame.utterance_text:
            return RobotMode.POLYPHARMACY_SAFETY_FOLLOWUP
        return RobotMode.EMERGENCY

    # 다약제 트리거
    if 18 <= hour <= 22 and frame.medication_action_detected:
        if frame.pill_count and frame.pill_count >= 5:
            # 다약제 복용 직후 → 30분 모니터링 모드
            return RobotMode.POLYPHARMACY_SAFETY_FOLLOWUP

    # 인지중재 시간대
    if 10 <= hour <= 18:
        return RobotMode.COGNITIVE_INTERVENTION

    return RobotMode.WELLNESS_CHECK


# ───────────────────────────────────────────────
# Layer 3 — Plan-to-Skill Mapping
# ───────────────────────────────────────────────

def execute_polypharmacy_followup(
    frame: PerceptionFrame,
    ctx: PatientContext,
    robot: RobotHardware,
    drug_db: DrugDatabase,
    notify: NotificationService,
    llm: MockLLM,
) -> dict:
    """30분 다약제 사후 모니터링 실행.

    설계 원칙:
        관절염·거동제한 어르신은 로봇 쪽으로 *오지 않는다*. 로봇이 어르신께 *간다*.
        모든 인터랙션은 음성 + 디스플레이 시선 추적 기반.
        무릎 굽힘·손목 비틀기·일어서기를 일절 요구하지 않는다.

    Returns:
        outcome: {"escalated": bool, "reason": str, "vitals_summary": ...}
        — Layer 5 reflection이 회수해 학습에 사용한다.
    """
    # 환자 옆으로 이동, 시선 맞춤 (어르신이 일어서지 않아도 되도록)
    robot.move_to(f"{frame.location}_옆_1m")
    robot.gaze_at("patient.face")

    # 친화적 안내 — 약품명·용량은 절대 발화 금지
    greeting = "약 잘 드신 거 보였어요. 30분만 같이 있을게요."
    robot.say(llm.filter_response(greeting))

    # 약물 상호작용 사전 체크 (read-only)
    interactions = drug_db.check_interactions(ctx.medications())

    # 과거 부작용 + 관절염 낙상 이력 회상 (Layer 4)
    high_risk_patterns = [p for p in ctx.procedural_patterns
                          if "side_effect" in p.pattern_name]
    has_arthritis_fall_history = any(
        "fall" in p.pattern_name or "arthritis" in p.pattern_name
        for p in ctx.procedural_patterns
    )

    # 임계값 결정 — 부작용 패턴 또는 관절염 낙상 이력 있으면 sensitive 모드
    # 관절염 환자는 일반 노인보다 낙상 위험이 1.5~2배 높아 더 보수적 설정
    if high_risk_patterns or interactions or has_arthritis_fall_history:
        thresholds = {"hr_delta": 12, "facial_pallor": 0.3}
    else:
        thresholds = {"hr_delta": 18, "facial_pallor": 0.5}

    # 30분 모니터링 시작
    monitor = robot.start_vitals_monitor(
        duration_min=30,
        signals=["HR", "SpO2", "facial_pallor", "speech_slur", "balance_loss"],
    )

    baseline_hr = frame.wearable_hr or 75
    escalated = False
    escalation_reason = None

    for reading in monitor.stream():
        # 임계값 초과 검사
        if abs(reading.hr - baseline_hr) > thresholds["hr_delta"]:
            escalated = True
            escalation_reason = f"HR delta {reading.hr - baseline_hr}"
        if reading.facial_pallor > thresholds["facial_pallor"]:
            escalated = True
            escalation_reason = "facial_pallor exceeded"

        if escalated:
            # 가족 알림 — 약품명·진단명 미포함, 객관적 사실만
            notify.notify(
                role="family",
                severity=Severity.MODERATE.value,
                payload={
                    "reason": escalation_reason,
                    "vitals_at_escalation": {
                        "hr": reading.hr,
                        "spo2": reading.spo2,
                    },
                    "patient_id": ctx.patient_id,
                    "location": frame.location,
                },
            )
            break

    return {
        "escalated": escalated,
        "reason": escalation_reason,
        "session_started_at": frame.timestamp.isoformat(),
        "thresholds_used": thresholds,
    }


# ───────────────────────────────────────────────
# Layer 4 — Memory write-back
# ───────────────────────────────────────────────

def record_episodic(ctx: PatientContext, frame: PerceptionFrame, outcome: dict) -> None:
    """이번 세션 사건을 장기 메모리에 기록."""
    episode = EpisodicMemory(
        memory_id=f"ep_{frame.timestamp.timestamp():.0f}",
        patient_id=ctx.patient_id,
        source=SignalSource.VISION,
        event_type="polypharmacy_safety_followup",
        timestamp=frame.timestamp,
        location=frame.location,
        symptom_category=SymptomCategory.GENERAL,
        severity=Severity.MODERATE if outcome["escalated"] else Severity.LOW,
        description=f"저녁 다약제 복용 후 30분 모니터링 ({frame.pill_count}알)",
        action_taken="monitor_30min" + ("+notify_family" if outcome["escalated"] else ""),
        outcome=outcome["reason"] or "no_escalation",
    )
    # 실제: DB insert
    logger.info(f"[Memory] episodic recorded: {episode.event_type}")


# ───────────────────────────────────────────────
# Layer 5 — Self-reflection (별도 배치, 주 1회 실행)
# ───────────────────────────────────────────────

def reflect_weekly(patient_id: str) -> None:
    """지난 7일 episodic 메모리를 모아 임계값·패턴 갱신.

    의료 안전 측면에서 *완전 자동 자기 수정 금지*.
    배치 결과는 임상 책임자(RN/MD) 검토 후 적용.
    """
    # 실제: DB에서 지난 7일 EpisodicMemory 조회
    # 1) 오탐(가족이 '문제 없음' 회신) → 임계값 상향
    # 2) 미탐(사후 의료진 코멘트로 위험 누락 발견) → 임계값 하향
    # 3) 반복 패턴 → ProceduralMemory에 추가 또는 observed_count 증가
    logger.info(f"[Reflection] weekly batch queued for {patient_id} — pending RN review")


# ───────────────────────────────────────────────
# Orchestrator — 한 사이클 main
# ───────────────────────────────────────────────

def run_one_cycle(
    sensors: dict[str, Any],
    ctx: PatientContext,
    robot: RobotHardware,
    drug_db: DrugDatabase,
    notify: NotificationService,
    llm: MockLLM,
) -> Optional[dict]:
    """ROSA 5계층을 한 번 순회한다."""
    # Layer 1
    frame = perceive(sensors)
    logger.info(f"[L1] perceived: {frame}")

    # 단기 메모리에 발화 기록
    if frame.utterance_text:
        ctx.short_term.recent_utterances.append(
            Utterance(role="patient", text=frame.utterance_text, timestamp=frame.timestamp)
        )
        ctx.short_term.trim_utterances()

    # Layer 2
    mode = plan(frame, ctx, llm)
    ctx.short_term.current_mode = mode
    ctx.short_term.triage_history.append(
        TriageDecision(
            timestamp=frame.timestamp, mode=mode,
            rationale=f"hour={frame.timestamp.hour}, pill_count={frame.pill_count}",
        )
    )
    logger.info(f"[L2] mode decided: {mode}")

    # Layer 3 — 모드별 분기
    if mode == RobotMode.POLYPHARMACY_SAFETY_FOLLOWUP:
        outcome = execute_polypharmacy_followup(frame, ctx, robot, drug_db, notify, llm)

        # Layer 4 — write-back
        record_episodic(ctx, frame, outcome)
        return outcome

    # 다른 모드는 별도 실행 함수 (cognitive_intervention, emergency 등)
    logger.info(f"[L3] mode {mode} — separate handler not shown in this scenario")
    return None


# ───────────────────────────────────────────────
# Demo entry — 부트캠프 발표용
# ───────────────────────────────────────────────

def demo() -> None:
    """발표 데모: 저녁 7시 42분, 환자가 약 7알 복용."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Mock 환자 컨텍스트
    from rosa_healthcare.memory_schema import (
        EpisodicMemory, ProceduralMemory, SemanticMemory, ShortTermMemory,
    )

    ctx = PatientContext(
        patient_id="lee_jeongja",
        short_term=ShortTermMemory(
            session_id="sess_2026_04_30_evening",
            patient_id="lee_jeongja",
            started_at=datetime.now(timezone.utc),
        ),
        semantic_facts={
            "medications": SemanticMemory(
                memory_id="sem_meds_001",
                patient_id="lee_jeongja",
                source=SignalSource.EMR,
                fact_key="medications",
                fact_value="amlodipine,furosemide,spironolactone,digoxin,amitriptyline,tramadol,zolpidem",
            )
        },
        procedural_patterns=[
            ProceduralMemory(
                memory_id="proc_001",
                patient_id="lee_jeongja",
                source=SignalSource.FAMILY,
                pattern_name="evening_dizziness_side_effect",
                trigger_condition={"time_window": "19:00-21:00"},
                typical_response="soft_voice + family_pre_alert",
                observed_count=2,
            ),
            ProceduralMemory(
                memory_id="proc_002",
                patient_id="lee_jeongja",
                source=SignalSource.SELF_REPORT,
                pattern_name="arthritis_knee_pain_mobility_limit",
                trigger_condition={"location": "kitchen_distance_5m"},
                typical_response="robot_brings_meds_to_patient",
                observed_count=12,
            ),
        ],
    )

    # 데모: 저녁 7시 42분(KST)으로 고정 -> polypharmacy_safety_followup 분기 진입
    demo_time = datetime(2026, 4, 30, 19, 42, 0).astimezone()

    sensors = {
        "timestamp": demo_time,
        "vision_med_action": True,
        "vision_pill_count": 7,
        "audio_asr": "오늘 약 다 먹어야지",
        "spatial_location": "부엌",
        "wearable_hr": 78,
        "wearable_spo2": 97,
    }

    outcome = run_one_cycle(
        sensors=sensors,
        ctx=ctx,
        robot=RobotHardware(),
        drug_db=DrugDatabase(),
        notify=NotificationService(),
        llm=MockLLM(),
    )
    print("\n=== Demo outcome ===")
    print(outcome)


if __name__ == "__main__":
    demo()
