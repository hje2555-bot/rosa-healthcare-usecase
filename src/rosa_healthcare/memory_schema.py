"""삼온 케어 로봇 — 메모리 스키마 (Layer 4).

ROSA 5계층 중 Layer 4 메모리 계층의 단기·장기 메모리 데이터 모델.
의료법 22조·개인정보보호법을 고려한 보존 기간 필드를 포함한다.

설계 원칙:
    1) 단기 메모리는 인메모리(휘발성), 장기 메모리는 영속 저장소(DB).
    2) 모든 장기 메모리 항목은 retention_until 필드 필수 (5년 자동 만료).
    3) 환자 동의 철회 시 patient_id 기반 즉시 삭제 가능 구조.
    4) Episodic / Semantic / Procedural 세 종류 메모리 분리.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ───────────────────────────────────────────────
# 공통 타입
# ───────────────────────────────────────────────

class SignalSource(str, Enum):
    """1계층 perception 데이터 출처."""
    SELF_REPORT = "self_report"     # 환자 발화
    WEARABLE = "wearable"           # Apple Watch, 오우라링 등
    VISION = "vision"               # 카메라 영상 분석
    AUDIO = "audio"                 # 마이크 음성·기침 분석
    LIDAR = "lidar"                 # 낙상·이동 감지
    EMR = "emr"                     # 의료기관 EMR (read-only)
    FAMILY = "family"               # 가족 보고


class SymptomCategory(str, Enum):
    """증상 분류 (의료법 27조 회피 — 진단명이 아니라 증상 그룹)."""
    CARDIOVASCULAR = "cardiovascular"     # 심박 이상, 흉통
    NEUROLOGICAL = "neurological"         # 어지러움, 의식 변화, 언어장애
    MUSCULOSKELETAL = "musculoskeletal"   # 낙상, 근력 저하, 관절통
    PSYCHIATRIC = "psychiatric"           # 우울, 불안, 수면 장애
    GASTROINTESTINAL = "gastrointestinal" # 식욕, 복통, 변비
    GENITOURINARY = "genitourinary"       # 배뇨 빈도, 부종
    GENERAL = "general"                   # 피로, 발열, 통증 일반


class Severity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RobotMode(str, Enum):
    """2계층 plan 결정 결과 — 작동 모드."""
    IDLE = "idle"
    COGNITIVE_INTERVENTION = "cognitive_intervention"
    POLYPHARMACY_REMINDER = "polypharmacy_reminder"
    POLYPHARMACY_SAFETY_FOLLOWUP = "polypharmacy_safety_followup"
    EMERGENCY = "emergency"
    WELLNESS_CHECK = "wellness_check"


# ───────────────────────────────────────────────
# 단기 메모리 (인메모리, 세션 단위)
# ───────────────────────────────────────────────

class Utterance(BaseModel):
    """대화 한 턴."""
    role: str                       # "patient" | "robot"
    text: str
    timestamp: datetime


class TriageDecision(BaseModel):
    """본 세션 내에서 시스템이 내린 트리아지 결정."""
    timestamp: datetime
    mode: RobotMode
    rationale: str                   # 결정 근거 (감사용)
    skills_invoked: list[str] = Field(default_factory=list)


class ShortTermMemory(BaseModel):
    """현재 대화 세션 단위 메모리."""
    session_id: str
    patient_id: str
    started_at: datetime

    # 최근 N턴 발화 (N=10)
    recent_utterances: list[Utterance] = Field(default_factory=list)

    # 현재 모드 + 목표
    current_mode: RobotMode = RobotMode.IDLE
    current_goal: Optional[str] = None

    # 본 세션 트리아지 이력
    triage_history: list[TriageDecision] = Field(default_factory=list)

    # 최근 30분 활력 추세 (slot 기반 ring buffer)
    recent_vitals_30min: list[dict] = Field(default_factory=list)

    def trim_utterances(self, max_n: int = 10) -> None:
        """N턴 초과 시 가장 오래된 발화부터 폐기."""
        if len(self.recent_utterances) > max_n:
            self.recent_utterances = self.recent_utterances[-max_n:]


# ───────────────────────────────────────────────
# 장기 메모리 (영속 저장, 환자 전체 기간)
# ───────────────────────────────────────────────

DEFAULT_RETENTION_YEARS = 5


def _default_retention() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=365 * DEFAULT_RETENTION_YEARS)


class LongTermMemoryBase(BaseModel):
    """모든 장기 메모리 항목의 공통 필드.

    개인정보보호법 + 의료법 21조의2 준수:
        - retention_until 도래 시 자동 삭제
        - 환자 동의 철회 시 patient_id 기반 cascade delete
    """
    memory_id: str
    patient_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: SignalSource
    retention_until: datetime = Field(default_factory=_default_retention)


class EpisodicMemory(LongTermMemoryBase):
    """사건 단위 메모리 — 일일 복약, 부작용, 낙상, 인지중재 세션 등."""
    event_type: str                          # 예: "medication_taken", "fall", "cst_session"
    timestamp: datetime
    location: Optional[str] = None
    symptom_category: Optional[SymptomCategory] = None
    severity: Optional[Severity] = None
    description: str
    action_taken: Optional[str] = None       # 시스템이 취한 행동 (감사용)
    outcome: Optional[str] = None            # 사후 회수된 결과 (Layer 5 학습용)


class SemanticMemory(LongTermMemoryBase):
    """환자 특이 사실 — 처방약, 알레르기, 가족, 선호 콘텐츠."""
    fact_key: str                            # 예: "medications", "allergies", "favorite_song"
    fact_value: str                          # JSON 문자열 가능 (구조화 사실)
    confidence: float = 1.0                  # LLM 추출 시 0.0~1.0


class ProceduralMemory(LongTermMemoryBase):
    """학습된 행동 패턴 — '이 환자는 X 시점에 Y 호소' 같은 규칙."""
    pattern_name: str                         # 예: "evening_dizziness_after_amlodipine"
    trigger_condition: dict                  # 예: {"time_window": "19:00-21:00", "med": "amlodipine"}
    typical_response: str                    # 예: "soft_voice + family_pre_alert"
    observed_count: int = 1                  # 누적 관찰 횟수
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ───────────────────────────────────────────────
# 환자 컨텍스트 통합 뷰
# ───────────────────────────────────────────────

class PatientContext(BaseModel):
    """RAG 검색 시 한 번에 묶이는 환자 통합 컨텍스트.

    Layer 2 plan 단계와 Layer 3 skill 단계에서 참조한다.
    Layer 5 reflection 시 outcome을 기준으로 procedural memory가 갱신된다.
    """
    patient_id: str
    short_term: ShortTermMemory
    recent_episodes: list[EpisodicMemory] = Field(default_factory=list)
    semantic_facts: dict[str, SemanticMemory] = Field(default_factory=dict)
    procedural_patterns: list[ProceduralMemory] = Field(default_factory=list)

    def medications(self) -> list[str]:
        """현재 처방약 리스트 (semantic memory에서)."""
        meds = self.semantic_facts.get("medications")
        if meds:
            # 실제로는 JSON 파싱
            return meds.fact_value.split(",")
        return []

    def has_pattern(self, pattern_name: str) -> bool:
        return any(p.pattern_name == pattern_name for p in self.procedural_patterns)
