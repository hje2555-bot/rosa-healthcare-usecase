# Samon Care Robot

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Built on NASA-JPL ROSA](https://img.shields.io/badge/Built%20on-NASA--JPL%20ROSA-orange.svg)](https://github.com/nasa-jpl/rosa)
[![Status: Concept Exploration](https://img.shields.io/badge/Status-Concept%20Exploration-yellow.svg)](#-disclaimer)
[![ROSA 5-Layer Mapped](https://img.shields.io/badge/ROSA-5--Layer%20Mapped-purple.svg)](docs/01-architecture-mapping.md)
[![Memory Workflow](https://img.shields.io/badge/Workflow-5--Step%20Memory%20Generation-green.svg)](docs/06-memory-generation-workflow.md)
[![Domain](https://img.shields.io/badge/Domain-Elderly%20Home%20Care-red.svg)](docs/00-executive-summary.md)
[![Upstream PR](https://img.shields.io/badge/Upstream%20PR-nasa--jpl%2Frosa%2382-lightgrey.svg)](https://github.com/nasa-jpl/rosa/pull/82)

> *Personal domain-extension exploration. Concept proposal, not an official deliverable.*
> Extending NASA-JPL ROSA's 5-layer agentic architecture as a home care use case targeting CLOi-class service robot platforms.
> *Cognitive stimulation by day, polypharmacy safety monitoring by night.*

## ⚠ Disclaimer

This repository is a **personal domain-extension exploration** by the author during participation in an AI service development program. It is **not an official deliverable**, **not endorsed or sponsored** by any company, and any references to specific commercial platforms or LLMs represent **technical compatibility scenarios, not business commitments**. All roadmap timelines, market projections, and channel claims are **hypothetical scenarios**, not real partnership terms.

**Author**: Jieun Hwang — RN, MS in Integrative Medicine
**Built on**: [nasa-jpl/rosa](https://github.com/nasa-jpl/rosa) (Apache 2.0)
**Upstream contribution**: [nasa-jpl/rosa#82](https://github.com/nasa-jpl/rosa/pull/82)

---

## 1. Project Position — Where Three Partners Meet

| Partner | Asset | Use in this project |
|---------|-------|----------------------|
| **Hardware reference platform** | CLOi-class service robot (validated autonomous navigation + HRI service-robot platform) | Hardware compatibility hypothesis (no actual partnership) |
| **Upstage** | Solar LLM (best-in-class Korean, medical-domain fine-tunable), Document AI | Reasoning + memory RAG backend |
| **SeSAC** | Korean youth talent pool, prototyping infrastructure | Build + integration |
| **Domain Expertise** | 8 yrs clinical (ER, ICU, outpatient, CRM) + 5 yrs public health + 5 yrs 1:1 VIP nursing at a premium membership clinic + MS Integrative Medicine | Home care scenarios, clinical guardrails, content curation |

This is **not a startup pitch and not a partnership proposal** — it is a personal exploration of a CLOi-class service robot platform applied to the home care domain.

## 2. What We Built

A **two-mode single-robot concept** designed to run on a CLOi-class service robot platform.

| Mode | Time of Day | Function |
|------|-------------|----------|
| Cognitive Intervention Mode | Daytime (10:00 — 18:00) | Non-pharmacological cognitive stimulation therapy (CST) using Korean traditional dance, classical music, and generation-specific reminiscence content |
| Polypharmacy Safety Monitoring Mode | Evening (18:00 — 22:00) | 30-minute post-medication monitoring of facial expression, voice, and heart rate; automatic adverse-event detection |

*"Samon (三溫)"* = **three warmths**: warmth of the body (medication safety) + warmth of the mind (cognitive intervention) + warmth of family (connection).
A working project codename; any commercial branding belongs to a future hardware partner if one is established.

## 3. Why Now — Three Forces Aligned

### Policy: Korea's Integrated Care Act (effective March 20, 2026)
KRW 13 trillion budget. 200 home medical care centers in Phase 1, expanding to 600 by 2027. Policy intent: *"keep medical and care services unbroken outside the hospital"* — the first regulatory window for service robots to enter Korean homes at scale.

### Technology: ROSA + CLOi-class service robot platform + Upstage Solar
- ROSA's 5-layer agentic architecture (perception · planning · skill · memory · self-reflection) was originally designed for *turtle coordinates* but maps directly onto *patient clinical data + robot sensors and motors*.
- CLOi-class service-robot autonomous navigation and HRI, validated in hospitality and service domains, can be hypothetically transferred to the home environment.
- Upstage Solar is the most accurate Korean-language LLM for elderly speech and patient self-reports, with data sovereignty advantages over foreign models.

### Market: 9.5M elderly, 4.8M with arthritis, 230K ER visits from drug adverse events
- TAM: KRW 5.7T (9.5M elderly × KRW 50K/month)
- B2C + B2B (long-term care facilities, home medical care centers) + Global (hypothetical Japan, Southeast Asia, Middle East distribution channels)

## 4. Why It Fits Elderly with Arthritis and Mobility Limitations

Korean adults aged 65+ have **~50% arthritis prevalence (~4.8M people)**. Knee and hip osteoarthritis make daily mobility — *"the 5 meters from sofa to kitchen"* — a barrier. Mobility limitation cascades into reduced outings, cognitive understimulation, accelerated dementia, and elevated fall risk. **Polypharmacy + cognitive decline + fall risk accumulate in the same patient**, and Samon addresses all three on one platform.

Five concrete fits:
1. **The robot brings medications to the elder** — autonomous navigation delivers the pill case to the living room sofa; the 5-meter kitchen trip disappears.
2. **All interaction is voice-first** — no need to bend the knee to operate a phone or twist the wrist for a wearable.
3. **Cognitive intervention happens in the living room** — 30 minutes a day of Korean traditional dance and reminiscence content, no outing required.
4. **Falls are detected by LiDAR** — no wristwatch, no phone needed; 4-channel sensor fusion plus automatic 119 (emergency services) escalation.
5. **Polypharmacy follow-up monitors alongside** — 30-minute post-medication detection of dizziness and cardiac events, alerting family *before* a fall.

## 5. ROSA 5-Layer → Samon Care Robot Mapping

| Layer | ROSA Original (TurtleSim) | Samon Adaptation (on CLOi-class platform) |
|-------|---------------------------|--------------------------------|
| 1. Multi-modal Perception | Turtle coordinates and obstacles | service robot camera, microphone array, LiDAR, touch + external wearables (6 channels) |
| 2. Goal-to-Plan Translation | "Draw a star" → coordinate sequence | Upstage Solar maps *time-of-day + voice intent + patient state* → cognitive / polypharmacy / emergency branch |
| 3. Plan-to-Skill Mapping | move/turn API | service robot motors, display, speaker + notification + drug database + EMR API |
| 4. Memory & Context | Prior shapes remembered | Per-patient medications, family contacts, preferred music, cognitive intervention patterns persisted long-term |
| 5. Self-reflection Learning | Compress failed shapes | Content efficacy learning + alert threshold auto-tuning (RN/MD review before deployment) |

Detailed mapping: [docs/01-architecture-mapping.md](docs/01-architecture-mapping.md)

## 6. Global Competitive Landscape — An Empty Home Care Category

| Solution | Country | Position | Limitation |
|----------|---------|----------|------------|
| Paro | Japan | Therapeutic seal robot | No proven cognitive intervention efficacy |
| ElliQ | Israel/USA | Voice-based elderly companion | No clinical monitoring |
| Buddy | France | Home companion robot | No medical-domain guardrails |
| Robear | Japan | Hospital lifting assistant | Not designed for home use |
| **Samon (CLOi-class platform)** | **Korea** | **Clinical monitoring + Korean-content CST** | — |

Differentiator: *Foreign home robots stop at emotional support; domestic products stop at simple reminders. Samon is the first category combining clinical monitoring with K-content cognitive intervention.*

## 7. 3-Phase Hypothetical Roadmap

| Phase | Period | Deliverable | Track |
|-------|--------|-------------|-------|
| **Phase 0** | 2026 Q3 (3 months) | **Cognitive intervention module standalone launch + extended collaboration kickoff (hypothetical)** | Personal exploration |
| **Phase 1** | 2026 Q4 — 2027 Q2 | **CLOi-class platform Home Care beta (hypothetical)** | Hardware partner internal validation + 50-household pilot, KFDA SaMD Class 2 |
| **Phase 2** | 2027 Q3 + | **Volume production + global launch (hypothetical)** | Global home appliance channels (Japan, Southeast Asia, Middle East) |

## 8. Three Real-World Scenarios

| ID | Title | Source Expertise |
|----|-------|------------------|
| A | Polypharmacy post-medication safety monitoring (primary) | 8 years ER + cancer center 1:1 nursing |
| B | Korean-dance reminiscence cognitive intervention (Phase 0) | Integrative medicine MS + K-content asset |
| C | Integrated emergency: fall → family → 119 | ER golden-hour operations |

Details: [docs/02](docs/02-scenario-a-polypharmacy.md), [docs/03](docs/03-scenario-b-cognitive-care.md), [docs/04](docs/04-scenario-c-emergency-bridge.md)

## 9. Regulatory and Safety Posture

The system performs **no diagnosis and no prescription**. Built from day one to comply with:
- Korean Medical Act Article 27 (prohibition of unlicensed medical practice)
- KFDA Software-as-a-Medical-Device guidelines (Class 1 in Phase 0; Class 2 from Phase 1)
- Personal Information Protection Act + Medical Act Article 21-2 (electronic medical records)
- Integrated Care Act (2026)

Detailed regulatory review: [docs/05](docs/05-regulatory-considerations.md)

## 10. License and Acknowledgements

- License: **Apache 2.0** — same as NASA-JPL ROSA
- Built on: [nasa-jpl/rosa](https://github.com/nasa-jpl/rosa) by Jet Propulsion Laboratory, NASA
- Hardware reference platform: **CLOi-class service robot**
- LLM partner: **Upstage Solar**
- Program: **Upstage × SeSAC AI Service Development Project — Corporate Collaboration Mission with LG Electronics (2026)**
- Upstream PR: [nasa-jpl/rosa#82](https://github.com/nasa-jpl/rosa/pull/82)

## 11. Contact

- GitHub: [@hje2555-bot