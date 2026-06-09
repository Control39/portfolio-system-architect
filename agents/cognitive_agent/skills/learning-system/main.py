"""
Система самообучения: записывает опыт агентов, анализирует прогресс, помогает улучшать алгоритмы.
"""

import json
import os
from datetime import datetime
from pathlib import Path

LOG_FILE = "apps/cognitive_agent/metrics/learning-log.json"


class LearningSystem:
    def __init__(self):
        Path("apps/cognitive_agent/metrics").mkdir(parents=True, exist_ok=True)
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                json.dump([], f)

    def log(self, skill: str, success: bool, duration_ms: int, details: dict = None):
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "skill": skill,
            "status": "success" if success else "failure",
            "duration_ms": duration_ms,
            "details": details or {},
        }
        with open(LOG_FILE, "r+") as f:
            data = json.load(f)
            data.append(record)
            f.seek(0)
            json.dump(data, f, indent=2)
        print(f"🧠 {skill}: опыт сохранён в learning-log.json")

    def get_trend(self, skill: str):
        """Анализирует прогресс по конкретному скиллу"""
        if not os.path.exists(LOG_FILE):
            return {"count": 0, "success_rate": 0}
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
        skill_logs = [l for l in logs if l["skill"] == skill]
        successes = [l for l in skill_logs if l["status"] == "success"]
        rate = len(successes) / len(skill_logs) * 100 if skill_logs else 0
        return {
            "count": len(skill_logs),
            "success_rate": round(rate, 1),
            "last_run": skill_logs[-1]["timestamp"] if skill_logs else None,
        }


if __name__ == "__main__":
    learner = LearningSystem()
    learner.log("marker-extraction", success=True, duration_ms=2150, details={"markers_found": 9})
    learner.log(
        "code-quality-auditor", success=False, duration_ms=5400, details={"error": "coverage < 85%"}
    )
    print("\n📈 Прогресс:")
    for skill in ["marker-extraction", "task-planner", "project-scanner"]:
        trend = learner.get_trend(skill)
        print(f"  {skill}: {trend}")
