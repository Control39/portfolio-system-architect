import logging
from src.models.responses import GapItem
from typing import Dict, List

logger = logging.getLogger(__name__)

class GapCalculator:
    def __init__(self, domain_weights: Dict[str, float]):
        self.domain_weights = domain_weights
        logger.info(f"⚙️ Calculator initialized with weights: {domain_weights}")

    def calculate(self, current_skills: Dict[str, int], target_skills: Dict[str, int]) -> List[GapItem]:
        """
        Вычисляет разрывы между текущими и целевыми навыками.
        current_skills: {"python": 50, "docker": 30}
        target_skills: {"python": 80, "docker": 80, "k8s": 60}
        """
        gaps = []
        target_set = set(target_skills.keys())
        current_set = set(current_skills.keys())
        
        # 1. Находим навыки, которых нет вообще или уровень ниже
        for skill, target_level in target_skills.items():
            current_level = current_skills.get(skill, 0)
            
            if current_level < target_level:
                # Определяем домен (упрощенно: python_dev -> python)
                domain = skill.split("_")[0] if "_" in skill else skill
                weight = self.domain_weights.get(domain, 1.0)
                
                # Формула приоритета: (Разрыв уровня) * (Вес домена)
                gap_score = (target_level - current_level) * weight
                
                gaps.append(GapItem(
                    skill_id=skill,
                    skill_name=skill.replace("_", " ").title(),
                    current_level=current_level,
                    target_level=target_level,
                    priority_score=gap_score,
                    estimated_hours=(target_level - current_level) * 2  # Грубая эвристика
                ))
        
        # 2. Сортируем по важности (priority_score desc)
        gaps.sort(key=lambda x: x.priority_score, reverse=True)
        
        logger.info(f"🧠 Calculated {len(gaps)} gaps")
        return gaps