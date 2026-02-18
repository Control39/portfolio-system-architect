# Генератор портфолио для IT Compass.
# Методология "Объективные маркеры компетенций"
# ¬© 2025 Ekaterina Kudelya. CC BY-ND 4.0
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# –§—É–Ω–∫—Ü–∏—è –¥–ª—è –æ–ø—Ä–µ–¥–µ–ª–µ–Ω–∏—è –∫–æ–¥–∏—Ä–æ–≤–∫–∏ —Ñ–∞–π–ª–∞

class PortfolioGenerator:
    def __init__(self, markers_dir: str = "src/data/markers", progress_file: str = "src/data/user_progress.json", output_file: str = "docs/my_portfolio.md"):
                self.markers_dir = Path(markers_dir)
        self.progress_file = Path(progress_file)
        self.output_file = Path(output_file)
        self._markers_cache: Optional[Dict[str, Dict]] = None
    
    def generate_portfolio(self) -> bool:
        try:
            progress = self._load_progress()
            if not progress:
                return False
            
            completed_markers = self._load_all_markers()
            completed_markers_list = [
                marker for marker_id, marker in completed_markers.items()
                if marker_id in progress.get("completed_markers", [])
            ]
            
            if not completed_markers_list:
                print("\0x274C –ù–µ—Ç –≤—ã–ø–æ–ª–Ω–µ–Ω–Ω—ã—Ö –º–∞—Ä–∫–µ—Ä–æ–≤.")
                return False
            
            portfolio_content = self._create_portfolio_content(completed_markers_list)
            return self._save_portfolio(portfolio_content)
            
        except Exception as e:
            logger.error(f"–û—à–∏–±–∫–∞ –ø—Ä–∏ –≥–µ–Ω–µ—Ä–∞—Ü–∏–∏ –ø–æ—Ä—Ç—Ñ–æ–ª–∏–æ: {e}")
            print(f"\0x26A0Ô∏è –û—à–∏–±–∫–∞ –≥–µ–Ω–µ—Ä–∞—Ü–∏–∏: {e}")
            return False
    
    def _load_progress(self) -> Optional[Dict]:
        if not self.progress_file.exists():
            print("\0x26A0Ô∏è –§–∞–π–ª –ø—Ä–æ–≥—Ä–µ—Å—Å–∞ –æ—Ç—Å—É—Ç—Å—Ç–≤—É–µ—Ç.")
            return None
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
            
            if not isinstance(progress, dict):
                logger.error("–ù–µ–∫–æ—Ä—Ä–µ–∫—Ç–Ω–∞—è —Å—Ç—Ä—É–∫—Ç—É—Ä–∞ —Ñ–∞–π–ª–∞ –ø—Ä–æ–≥—Ä–µ—Å—Å–∞")
                return None
                
            return progress
        except json.JSONDecodeError as e:
            logger.error(f"–û—à–∏–±–∫–∞ –ø–∞—Ä—Å–∏–Ω–≥–∞ —Ñ–∞–π–ª–∞ –ø—Ä–æ–≥—Ä–µ—Å—Å–∞: {e}")
            return None
        except Exception as e:
            logger.error(f"–ù–µ–æ–∂–∏–¥–∞–Ω–Ω–∞—è –æ—à–∏–±–∫–∞ –ø—Ä–∏ –∑–∞–≥—Ä—É–∑–∫–µ –ø—Ä–æ–≥—Ä–µ—Å—Å–∞: {e}")
            return None
    
    def _load_all_markers(self) -> Dict[str, Dict]:
        if self._markers_cache is not None:
            return self._markers_cache
        
        markers = {}
        
        if not self.markers_dir.exists():
            logger.warning(f"–î–∏—Ä–µ–∫—Ç–æ—Ä–∏—è –º–∞—Ä–∫–µ—Ä–æ–≤ –Ω–µ –Ω–∞–π–¥–µ–Ω–∞: {self.markers_dir}")
            return markers
        
        try:
            for json_path in self.markers_dir.glob("*.json"):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        skill_data = json.load(f)
                    
                    skill_name = skill_data.get("skill_name", json_path.stem.capitalize())
                    
                    for level_data in skill_data.get("levels", {}).values():
                        for marker in level_data:
                            marker_copy = marker.copy()
                            marker_copy["skill_name"] = skill_name
                            markers[marker["id"]] = marker_copy
                            
                except json.JSONDecodeError as e:
                    logger.error(f"–û—à–∏–±–∫–∞ –ø–∞—Ä—Å–∏–Ω–≥–∞ —Ñ–∞–π–ª–∞ {json_path}: {e}")
                except Exception as e:
                    logger.error(f"–ù–µ–æ–∂–∏–¥–∞–Ω–Ω–∞—è –æ—à–∏–±–∫–∞ –ø—Ä–∏ –∑–∞–≥—Ä—É–∑–∫–µ {json_path}: {e}")
                    
        except Exception as e:
            logger.error(f"–ö—Ä–∏—Ç–∏—á–µ—Å–∫–∞—è –æ—à–∏–±–∫–∞ –ø—Ä–∏ –∑–∞–≥—Ä—É–∑–∫–µ –º–∞—Ä–∫–µ—Ä–æ–≤: {e}")
            
        self._markers_cache = markers
        return markers
    
    def _create_portfolio_content(self, completed_markers: List[Dict]) -> List[str]:
        by_skill = self._group_markers_by_skill(completed_markers)
        
        lines = [
            "# \0x1F4E3 –ú–æ—ë IT-–ø–æ—Ä—Ç—Ñ–æ–ª–∏–æ",
            "",
            f"> –°—Ñ–æ—Ä–º–∏—Ä–æ–≤–∞–Ω–æ –∞–≤—Ç–æ–º–∞—Ç–∏—á–µ—Å–∫–∏ —á–µ—Ä–µ–∑ [IT Compass](https://github.com/Control39/it-compass) "
            f"({datetime.now().strftime('%d.%m.%Y')})",
            "",
            f"> **–ú–µ—Ç–æ–¥–æ–ª–æ–≥–∏—è:** ¬© 2025 Ekaterina Kudelya, [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/)",
            "",
            "## \0x2705 –ü–æ–¥—Ç–≤–µ—Ä–∂–¥—ë–Ω–Ω—ã–µ –Ω–∞–≤—ã–∫–∏",
            ""
        ]
        
        for skill_name in sorted(by_skill.keys()):
            lines.append(f"### {skill_name}")
            for marker in by_skill[skill_name]:
                lines.append(f"- \0x2705 **{marker['marker']}**")
                if marker.get("validation"):
                    lines.append(f" > üîç –í–∞–ª–∏–¥–∞—Ü–∏—è: {marker['validation']}")
                
                if marker.get("priority") == "high":
                    lines.append(f" > ‚≠ê –í—ã—Å–æ–∫–∏–π –ø—Ä–∏–æ—Ä–∏—Ç–µ—Ç –¥–ª—è —Ç—Ä—É–¥–æ—É—Å—Ç—Ä–æ–π—Å—Ç–≤–∞")
                
                methodology_author = marker.get("methodology_author", "Ekaterina Kudelya")
                methodology_license = marker.get("methodology_license", "CC BY-ND 4.0")
                lines.append(f" > üìã –ú–µ—Ç–æ–¥–æ–ª–æ–≥–∏—è: ¬© {methodology_author}, {methodology_license}")
            lines.append("")
        
        lines.extend([
            "## \0x1F4D1 –†–µ–∫–æ–º–µ–Ω–¥–∞—Ü–∏–∏ –ø–æ –∏—Å–ø–æ–ª—å–∑–æ–≤–∞–Ω–∏—é",
            "",
            "- –ü—Ä–∏–∫–ª–∞–¥—ã–≤–∞–π—Ç–µ —Å–∫—Ä–∏–Ω—à–æ—Ç—ã –≤—ã–ø–æ–ª–Ω–µ–Ω–Ω—ã—Ö –ø—Ä–æ–µ–∫—Ç–æ–≤",
            "- –£–∫–∞–∑—ã–≤–∞–π—Ç–µ —Å—Å—ã–ª–∫–∏ –Ω–∞ GitHub —Ä–µ–ø–æ–∑–∏—Ç–æ—Ä–∏–∏",
            "- –ò—Å–ø–æ–ª—å–∑—É–π—Ç–µ —ç—Ç–æ –ø–æ—Ä—Ç—Ñ–æ–ª–∏–æ –ø—Ä–∏ –æ—Ç–∫–ª–∏–∫–∞—Ö –Ω–∞ –≤–∞–∫–∞–Ω—Å–∏–∏",
            "",
            "> \0x1F6E0Ô∏è **–°–ª–µ–¥—É—é—â–∏–π —à–∞–≥:** –ü—Ä–æ–¥–æ–ª–∂–∞–π—Ç–µ –æ—Ç–º–µ—á–∞—Ç—å –≤—ã–ø–æ–ª–Ω–µ–Ω–Ω—ã–µ –º–∞—Ä–∫–µ—Ä—ã!"
        ])
        
        return lines
    
    def _group_markers_by_skill(self, markers: List[Dict]) -> Dict[str, List[Dict]]:
        grouped = {}
        for marker in markers:
            skill = marker.get("skill_name", "Other")
            grouped.setdefault(skill, []).append(marker)
        return grouped
    
    def _save_portfolio(self, content: List[str]) -> bool:
        try:
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            portfolio_text = '\n'.join(content)
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(portfolio_text)
            
            print(f"\0x2705 –ü–æ—Ä—Ç—Ñ–æ–ª–∏–æ —Å–æ—Ö—Ä–∞–Ω–µ–Ω–æ: {self.output_file.absolute()}")
            logger.info(f"–ü–æ—Ä—Ç—Ñ–æ–ª–∏–æ —É—Å–ø–µ—à–Ω–æ —Å–æ–∑–¥–∞–Ω–æ: {self.output_file}")
            return True
            
        except Exception as e:
            logger.error(f"–û—à–∏–±–∫–∞ –ø—Ä–∏ —Å–æ—Ö—Ä–∞–Ω–µ–Ω–∏–∏ –ø–æ—Ä—Ç—Ñ–æ–ª–∏–æ: {e}")
            print(f"\0x26A0Ô∏è –û—à–∏–±–∫–∞ –∑–∞–ø–∏—Å–∏: {e}")
            return False

def generate_portfolio():
    generator = PortfolioGenerator()
    return generator.generate_portfolio()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = generate_portfolio()
    
    if success:
        print("\n\0x1F389 –ü–æ—Ä—Ç—Ñ–æ–ª–∏–æ –≥–æ—Ç–æ–≤–æ! –§–∞–π–ª: docs/my_portfolio.md")
    else:
        print("\n\0x274C –ù–µ —É–¥–∞–ª–æ—Å—å —Å–æ–∑–¥–∞—Ç—å –ø–æ—Ä—Ç—Ñ–æ–ª–∏–æ.")