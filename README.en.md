# Samon Care Robot

> **Upstage × SeSAC AI Service Development (Plan → Implementation) Project — Corporate Collaboration Mission with LG Electronics.**
> Extending NASA-JPL ROSA's 5-layer agentic architecture onto the LG CLOi platform as a home care use case.
> *Cognitive stimulation by day, polypharmacy safety monitoring by night.*

**Program**: Upstage × SeSAC AI Service Development Project (end-to-end planning to implementation)
**Corporate Partner / Mission Owner**: LG Electronics
**Domain Lead**: Jieun Hwang — RN, MS in Integrative Medicine
**Built on**: [nasa-jpl/rosa](https://github.com/nasa-jpl/rosa) + LG CLOi platform + Upstage Solar LLM
**Upstream contribution**: [nasa-jpl/rosa#82](https://github.com/nasa-jpl/rosa/pull/82)

---

## 1. Project Position — Where Three Partners Meet

| Partner | Asset | Use in this project |
|---------|-------|----------------------|
| **LG Electronics** | CLOi service robots (validated autonomous navigation + HRI), ThinQ Care vision, global home appliance channels | Hardware platform + manufacturing + distribution |
| **Upstage** | Solar LLM (best-in-class Korean, medical-domain fine-tunable), Document AI | Reasoning + memory RAG backend |
| **SeSAC** | Korean youth talent pool, prototyping infrastructure | Build + integration |
| **Domain Expertise** | 8 yrs clinical (ER, ICU, outpatient, CRM) + 5 yrs public health + 5 yrs 1:1 VIP nursing (Cha-Eum) + MS Integrative Medicine | Home care scenarios, clinical guardrails, content curation |

This is **not a startup pitch** — it is a use case ready to enter LG CLOi's next product lineup as a Home Care track.

## 2. What We Built

A **two-mode single robot** running on LG CLOi hardware.

| Mode | Time of Day | Function |
|------|-------------|----------|
| Cognitive Intervention Mode | Daytime (10:00 — 18:00) | Non-pharmacological cognitive stimulation therapy (CST) using Korean traditional dance, classical music, and generation-specific reminiscence content |
| Polypharmacy Safety Monitoring Mode | Evening (18:00 — 22:00) | 30-minute post-medication monitoring of facial expression, voice, and heart rate; automatic adverse-event detection |

*"Samon (三溫)"* = **three warmths**: warmth of the body (medication safety) + warmth of the mind (cognitive intervention) + warmth of family (connection).
A working project codename; LG retains naming rights for commercialization.

## 3. Why Now — Three Forces Aligned

### Policy: Korea's Integrated Care Act (effective March 20, 2026)
KRW 13 trillion budget. 200 home medical care centers in Phase 1, expanding to 600 by 2027. Policy intent: *"keep medical and care services unbroken outside the hospital"* — the first regulatory window for LG CLOi to enter Korean homes at scale.

### Technology: ROSA + LG CLOi + Upstage Solar
- ROSA's 5-layer agentic architecture (perception · planning · skill · memory · self-reflection) was originally designed for *turtle coordinates* but maps directly onto *patient clinical data + robot sensors and motors*.
- LG CLOi's autonomous navigation and HRI, validated in hospitality and service domains, transfers to the home environment as a first product.
- Upstage Solar is the most accurate Korean-language LLM for elderly speech and patient self-reports, with data sovereignty advantages over foreign models.

### Market: 9.5M elderly, 4.8M with arthritis, 230K ER visits from drug adverse events
- TAM: KRW 5.7T (9.5M elderly × KRW 50K/month)
- B2C + B2B (long-term care facilities, home medical care centers) + Global (LG's Japan, Southeast Asia, Middle East channels)

## 4. Why It Fits Elderly with Arthritis and Mobility Limitations

Korean adults aged 65+ have **~50% arthritis prevalence (~4.8M people)**. Knee and hip osteoarthritis make daily mobility — *"the 5 meters from sofa to kitchen"* — a barrier. Mobility limitation cascades into reduced outings, cognitive understimulation, accelerated dementia, and elevated fall risk. **Polypharmacy + cognitive decline + fall risk accumulate in the same patient**, and Samon addresses all three on one platform.

Five concrete fits:
1. **The robot brings medications to the elder** — autonomous navigation delivers the pill case to the living room sofa; the 5-meter kitchen trip disappears.
2. **All interaction is voice-first** — no need to bend the knee to operate a phone or twist the wrist for a wearable.
3. **Cognitive intervention happens in the living room** — 30 minutes a day of Korean traditional dance and reminiscence content, no outing required.
4. **Falls are detected by LiDAR** — no wristwatch, no phone needed; 4-channel sensor fusion plus automatic 119 (emergency services) escalation.
5. **Polypharmacy follow-up monitors alongside** — 30-minute post-medication detection of dizziness and cardiac events, alerting family *before* a fall.

## 5. ROSA 5-Layer → Samon Care Robot Mapping

| Layer | ROSA Original (TurtleSim) | Samon Adaptation (on LG CLOi) |
|-------|---------------------------|--------------------------------|
| 1. Multi-modal Perception | Turtle coordinates and obstacles | LG CLOi camera, microphone array, LiDAR, touch + external wearables (6 channels) |
| 2. Goal-to-Plan Translation | "Draw a star" → coordinate sequence | Upstage Solar maps *time-of-day + voice intent + patient state* → cognitive / polypharmacy / emergency branch |
| 3. Plan-to-Skill Mapping | move/turn API | LG CLOi motors, display, speaker + notification + drug database + EMR API |
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
| **Samon (LG CLOi)** | **Korea** | **Clinical monitoring + Korean-content CST** | — |

Differentiator: *Foreign home robots stop at emotional support; domestic products stop at simple reminders. Samon is the first category combining clinical monitoring with K-content cognitive intervention.*

## 7. 3-Phase Roadmap (Aligned with LG CLOi Lineup)

| Phase | Period | Deliverable | Track |
|-------|--------|-------------|-------|
| **Phase 0** | 2026 Q3 (3 months) | **Cognitive intervention module standalone launch + extended-collaboration kickoff** | SeSAC × Upstage × LG joint |
| **Phase 1** | 2026 Q4 — 2027 Q2 | **LG CLOi for Home Care beta** | LG internal validation + 50-household pilot, KFDA SaMD Class 2 |
| **Phase 2** | 2027 Q3 + | **Volume production + LG global launch** | LG global channels (Japan, Southeast Asia, Middle East) |

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
- Hardware partner: **LG Electronics CLOi**
- LLM partner: **Upstage Solar**
- Program: **Upstage × SeSAC AI Service Development Project — Corporate Collaboration Mission with LG Electronics (2026)**
- Upstream PR: [nasa-jpl/rosa#82](https://github.com/nasa-jpl/rosa/pull/82)

## 11. Contact

- GitHub: [@hje2555-bot](https://github.com/hje2555-bot)
- Email: hje2555@gmail.com

---

*"What clinicians do not see at the bedside, AI sees even less. Domain comes first; the model follows. Hardware is the bridge."*
