"""삼온 케어 로봇 — 메모리 생성 워크플로우 (5단계).

학습 단계 표준 메모리 복원 워크플로우 5단계를 가정 돌봄 로봇 도메인에
적용한 실행 가능한 구현. 자세한 설명은 docs/06-memory-generation-workflow.md.

표준 5단계 워크플로우:
    Step 1: 기억 요소 요청하기
    Step 2: 기억 요소를 기반으로 가상 기억 생성
    Step 3: 가상 기억을 JSON으로 출력
    Step 4: "기억요소:가상기억"을 key-value 형태로 출력 (JSON)
    Step 5: N대의 로봇에 이식될 기억 만들기 (JSON 형식)

실행:
    cd rosa-healthcare-usecase
    PYTHONPATH=src python examples/memory_generation_workflow.py
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# 패키지 path 설정 (실제 배포 시 pip install로 대체)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rosa_healthcare.memory_schema import (  # noqa: E402
    EpisodicMemory,
    PatientContext,
    ProceduralMemory,
    RobotMode,
    SemanticMemory,
    Severity,
    ShortTermMemory,
    SignalSource,
    SymptomCategory,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("samon.workflow")

OUTPUT_DIR = Path(__file__).parent / "sample_memories"


# ═══════════════════════════════════════════════
# Step 1 — 기억 요소 요청 (Memory Element Elicitation)
# ═══════════════════════════════════════════════

MEMORY_ELEMENT_CATEGORIES: dict[str, list[str]] = {
    "demographics":       ["name", "age", "gender", "residence_type"],
    "medical_history":    ["diagnoses", "current_medications", "allergies",
                           "hospitalization_history", "pain_locations"],
    "family_emergency":   ["family_members", "primary_caregiver", "emergency_contacts",
                           "advance_care_planning"],
    "preferences":        ["favorite_music", "favorite_content", "dietary_preferences",
                           "religion"],
    "daily_routine":      ["wake_time", "sleep_time", "medication_schedule",
                           "outpatient_visits"],
    "pain_points":        ["arthritis_locations", "cognitive_weaknesses",
                           "outdoor_difficulty"],
    "emotional_triggers": ["trauma_topics_to_avoid", "recurrent_complaints",
                           "preferred_emotional_tone"],
}


def step1_request_memory_elements() -> dict[str, list[str]]:
    """Step 1. 사람의 기억을 구성하는 요소를 LLM(또는 사전 정의)으로 추출.

    실제 배포에서는 Upstage Solar 또는 Claude Sonnet 호출.
    여기서는 사전 큐레이션된 7개 카테고리 반환.
    """
    logger.info("[Step 1] 기억 요소 요청 — 7개 카테고리 추출")
    return MEMORY_ELEMENT_CATEGORIES


# ═══════════════════════════════════════════════
# Step 2 — 기억 요소 → 가상 기억 생성 (Persona Generation)
# ═══════════════════════════════════════════════

# 3 페르소나 시드 (LLM에게 줄 프롬프트의 골격)
PERSONA_SEEDS: list[dict[str, Any]] = [
    {
        "patient_id": "park_sunja",
        "name": "박순자",
        "age": 76, "gender": "F",
        "diagnoses": ["MCI", "knee_osteoarthritis", "hypertension"],
        "medications": ["amlodipine", "donepezil"],
        "key_history": "1971년 결혼, 미용실 30년 운영, 2024년 남편 사별",
        "preferences": {"favorite_song": "동백 아가씨 (이미자, 1964)",
                        "favorite_content": "한국무용·국악·세대별 회상 사진"},
        "scenario": "B - 한국무용 회상 인지중재",
    },
    {
        "patient_id": "kim_youngseok",
        "name": "김영석",
        "age": 78, "gender": "M",
        "diagnoses": ["heart_failure", "type2_diabetes", "depression",
                      "BPH", "insomnia"],
        "medications": ["furosemide", "spironolactone", "metformin", "sertraline",
                        "tamsulosin", "zolpidem", "aspirin"],
        "key_history": "은행원 35년, 2018년 은퇴, 2022년 심부전 진단",
        "preferences": {"favorite_song": "최희준 - 하숙생 (1966)",
                        "favorite_content": "가요무대·바둑 중계"},
        "scenario": "A - 다약제(polypharmacy) 사후 모니터링",
    },
    {
        "patient_id": "lee_jeongja",
        "name": "이정자",
        "age": 78, "gender": "F",
        "diagnoses": ["heart_failure", "depression", "knee_osteoarthritis",
                      "insomnia", "polypharmacy"],
        "medications": ["amlodipine", "furosemide", "spironolactone", "digoxin",
                        "amitriptyline", "tramadol", "zolpidem"],
        "key_history": "주부 평생, 자녀 출가 후 단독 거주, 2026년 1월 야간 낙상 1회",
        "preferences": {"favorite_song": "패티김 - 이별 (1972)",
                        "favorite_content": "TV 드라마·라디오"},
        "scenario": "C - 통합 응급 (낙상 → 가족 → 119)",
    },
]


def step2_generate_virtual_memories(seeds: list[dict[str, Any]]) -> list[PatientContext]:
    """Step 2. 시드 페르소나를 ROSA 5계층 메모리 구조로 확장.

    실제 배포에서는 LLM이 episodic 서사·procedural 패턴을 자연어 생성.
    여기서는 결정적 변환으로 검증 가능한 구조 생성.
    """
    logger.info("[Step 2] 3 페르소나에 가상 기억 생성")
    contexts: list[PatientContext] = []

    for seed in seeds:
        patient_id = seed["patient_id"]
        now = datetime.now(timezone.utc)

        ctx = PatientContext(
            patient_id=patient_id,
            short_term=ShortTermMemory(
                session_id=f"sess_{patient_id}_init",
                patient_id=patient_id,
                started_at=now,
            ),
            semantic_facts=_build_semantic_facts(patient_id, seed, now),
            recent_episodes=_build_episodic(patient_id, seed, now),
            procedural_patterns=_build_procedural(patient_id, seed, now),
        )
        contexts.append(ctx)

    return contexts


def _build_semantic_facts(pid: str, seed: dict[str, Any], now: datetime) -> dict[str, SemanticMemory]:
    """Semantic 메모리 = 환자 특이 사실의 key-value 집합 (Step 4의 그 형태)."""
    return {
        "demographics.name": SemanticMemory(
            memory_id=f"{pid}_sem_name", patient_id=pid, source=SignalSource.EMR,
            fact_key="demographics.name", fact_value=seed["name"],
        ),
        "demographics.age": SemanticMemory(
            memory_id=f"{pid}_sem_age", patient_id=pid, source=SignalSource.EMR,
            fact_key="demographics.age", fact_value=str(seed["age"]),
        ),
        "medical.diagnoses": SemanticMemory(
            memory_id=f"{pid}_sem_dx", patient_id=pid, source=SignalSource.EMR,
            fact_key="medical.diagnoses", fact_value=", ".join(seed["diagnoses"]),
        ),
        "medical.medications": SemanticMemory(
            memory_id=f"{pid}_sem_meds", patient_id=pid, source=SignalSource.EMR,
            fact_key="medical.medications", fact_value=", ".join(seed["medications"]),
        ),
        "preferences.favorite_song": SemanticMemory(
            memory_id=f"{pid}_sem_song", patient_id=pid, source=SignalSource.SELF_REPORT,
            fact_key="preferences.favorite_song",
            fact_value=seed["preferences"]["favorite_song"],
        ),
        "preferences.favorite_content": SemanticMemory(
            memory_id=f"{pid}_sem_content", patient_id=pid, source=SignalSource.SELF_REPORT,
            fact_key="preferences.favorite_content",
            fact_value=seed["preferences"]["favorite_content"],
        ),
        "biography.key_history": SemanticMemory(
            memory_id=f"{pid}_sem_bio", patient_id=pid, source=SignalSource.FAMILY,
            fact_key="biography.key_history", fact_value=seed["key_history"],
        ),
        "scenario.assigned": SemanticMemory(
            memory_id=f"{pid}_sem_scenario", patient_id=pid, source=SignalSource.SELF_REPORT,
            fact_key="scenario.assigned", fact_value=seed["scenario"],
        ),
    }


def _build_episodic(pid: str, seed: dict[str, Any], now: datetime) -> list[EpisodicMemory]:
    """Episodic 메모리 = 사건 기록 (LLM이 서사로 채울 자리)."""
    return [
        EpisodicMemory(
            memory_id=f"{pid}_ep_baseline",
            patient_id=pid,
            source=SignalSource.EMR,
            event_type="baseline_assessment",
            timestamp=now - timedelta(days=30),
            location="외래",
            symptom_category=SymptomCategory.GENERAL,
            severity=Severity.LOW,
            description=f"{seed['name']} 첫 등록 평가, 진단 {seed['diagnoses'][0]}",
            action_taken="enrollment",
            outcome="완료",
        ),
    ]


def _build_procedural(pid: str, seed: dict[str, Any], now: datetime) -> list[ProceduralMemory]:
    """Procedural 메모리 = 학습된 행동 패턴 (자기반성 학습이 누적)."""
    patterns: list[ProceduralMemory] = []

    if "knee_osteoarthritis" in seed["diagnoses"]:
        patterns.append(ProceduralMemory(
            memory_id=f"{pid}_proc_arthritis",
            patient_id=pid, source=SignalSource.SELF_REPORT,
            pattern_name="arthritis_knee_pain_mobility_limit",
            trigger_condition={"location": "kitchen_distance_5m"},
            typical_response="robot_brings_meds_to_patient",
            observed_count=12,
        ))

    if len(seed["medications"]) >= 5:
        patterns.append(ProceduralMemory(
            memory_id=f"{pid}_proc_polypharm",
            patient_id=pid, source=SignalSource.EMR,
            pattern_name="polypharmacy_evening_risk_window",
            trigger_condition={"time_window": "19:00-21:00",
                               "med_count": len(seed["medications"])},
            typical_response="post_med_30min_monitoring",
            observed_count=8,
        ))

    if "MCI" in seed["diagnoses"]:
        patterns.append(ProceduralMemory(
            memory_id=f"{pid}_proc_cst_response",
            patient_id=pid, source=SignalSource.SELF_REPORT,
            pattern_name="cst_korean_dance_positive_response",
            trigger_condition={"content_category": "korean_dance"},
            typical_response="extend_session_to_30min",
            observed_count=5,
        ))

    return patterns


# ═══════════════════════════════════════════════
# Step 3 — JSON 출력
# ═══════════════════════════════════════════════

def step3_serialize_to_json(contexts: list[PatientContext]) -> list[dict]:
    """Step 3. PatientContext → JSON-serializable dict."""
    logger.info("[Step 3] 가상 기억을 JSON으로 직렬화")
    return [json.loads(ctx.model_dump_json()) for ctx in contexts]


# ═══════════════════════════════════════════════
# Step 4 — Key-Value 포맷
# ═══════════════════════════════════════════════

def step4_to_key_value(contexts: list[PatientContext]) -> list[dict[str, str]]:
    """Step 4. *기억요소:가상기억* 을 key-value 형태로 출력.

    원본 미션 도식의 4번 박스가 정확히 이 변환.
    semantic_facts 에서 fact_key → fact_value 의 단순 dict 추출.
    """
    logger.info("[Step 4] key-value 형태 변환")
    kv_list = []
    for ctx in contexts:
        kv = {
            sem.fact_key: sem.fact_value
            for sem in ctx.semantic_facts.values()
        }
        kv_list.append(kv)
    return kv_list


# ═══════════════════════════════════════════════
# Step 5 — 3대 로봇 메모리 파일 생성
# ═══════════════════════════════════════════════

def step5_save_three_robot_memories(
    contexts: list[PatientContext], kv_list: list[dict[str, str]]
) -> list[Path]:
    """Step 5. 3개 로봇별 JSON 파일을 디스크에 저장."""
    logger.info("[Step 5] 3대 로봇 메모리 파일 생성")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    saved = []

    for i, (ctx, kv) in enumerate(zip(contexts, kv_list), start=1):
        robot_id = f"samon_{i:03d}"
        filename = f"robot_{i}_{ctx.patient_id}.json"
        path = OUTPUT_DIR / filename

        payload = {
            "robot_id": robot_id,
            "patient_id": ctx.patient_id,
            "memory_format_version": "rosa_layer4_v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "key_value_summary": kv,                                  # Step 4 산출
            "full_memory": json.loads(ctx.model_dump_json()),         # Step 3 산출
        }

        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        saved.append(path)
        logger.info(f"  -> {filename}  ({len(kv)} key-value pairs, "
                    f"{len(ctx.recent_episodes)} episodic, "
                    f"{len(ctx.procedural_patterns)} procedural)")

    return saved


# ═══════════════════════════════════════════════
# Orchestrator
# ═══════════════════════════════════════════════

def run_workflow() -> None:
    """5단계 워크플로우 한 번에 실행."""
    print("=" * 60)
    print("삼온 케어 로봇 — 메모리 생성 워크플로우 (5단계)")
    print("출발점: 메모리 복원 워크플로우 (학습 표준) / 적용 도메인: 가정 돌봄")
    print("=" * 60)

    # Step 1
    elements = step1_request_memory_elements()
    print(f"\n  → 기억 요소 카테고리: {len(elements)}개\n"
          f"    {list(elements.keys())}")

    # Step 2
    contexts = step2_generate_virtual_memories(PERSONA_SEEDS)
    print(f"\n  → 페르소나 {len(contexts)}개 생성")

    # Step 3
    json_dicts = step3_serialize_to_json(contexts)
    print(f"\n  → JSON 직렬화 완료 ({len(json_dicts)} payload)")

    # Step 4
    kv_list = step4_to_key_value(contexts)
    print(f"\n  → key-value 변환 완료")
    for i, kv in enumerate(kv_list, start=1):
        print(f"    Robot {i} sample: name={kv['demographics.name']!r}, "
              f"diagnoses={kv['medical.diagnoses']!r}")

    # Step 5
    saved = step5_save_three_robot_memories(contexts, kv_list)
    print(f"\n  → 3대 로봇 메모리 파일 저장 완료")
    for p in saved:
        print(f"    {p.relative_to(OUTPUT_DIR.parent.parent)}")

    print("\n" + "=" * 60)
    print("워크플로우 완료. 각 JSON은 ROSA Layer 4 메모리로 직접 ingest 가능.")
    print("=" * 60)


if __name__ == "__main__":
    run_workflow()
