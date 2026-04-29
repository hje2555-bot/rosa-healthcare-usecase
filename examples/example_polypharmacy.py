"""삼온 케어 로봇 — 시나리오 A 실행 예시.

다음 명령으로 실행:
    cd rosa-healthcare-usecase
    pip install -r requirements.txt
    python -m examples.example_polypharmacy
또는:
    PYTHONPATH=src python examples/example_polypharmacy.py
"""

import sys
from pathlib import Path

# 패키지 path 설정 (실제 배포 시 pip install로 대체)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rosa_healthcare.scenario_a import demo

if __name__ == "__main__":
    demo()
