import json
import os
from datetime import datetime
from typing import Dict, List, Any

class CompetencyTracker:
    def __init__(self, data_file: str = 'user_progress.json'):
        self.data_file = data_file
        self.user_progress = self.load_progress()
        self.markers = self.load_markers()
    
    def load_markers(self) -> Dict[str, Dict]:
        # Stub markers
        return {
            'python_basics': {'name': 'Python Basics', 'description': 'Intro', 'category': 'backend_development', 'difficulty': 1, 'estimated_time': '2h'},
            'git_fundamentals': {'name': 'Git', 'description': 'Basics', 'category': 'devops', 'difficulty': 1, 'estimated_time': '1h'},
            # Add more...
        }
    
    def load_progress(self, file_path: str = None) -> Dict[str, Any]:
        file = file_path or self.data_file
        if os.path.exists(file):
            with open(file, 'r') as f:
                return json.load(f)
        return {'user_id': 'default', 'completed_markers': [], 'last_updated': datetime.now().isoformat()}
    
    def mark_completed(self, marker_id: str) -> bool:
        if marker_id not in self.user_progress['completed_markers']:
            self.user_progress['completed_markers'].append(marker_id)
            self.user_progress['last_updated'] = datetime.now().isoformat()
            return True
        return False
    
    def is_completed(self, marker_id: str) -> bool:
        return marker_id in self.user_progress['completed_markers']
    
    def get_statistics(self) -> Dict:
        total = len(self.markers)
        completed = len(self.user_progress['completed_markers'])
        return {
            'total_markers': total,
            'completed_markers': completed,
            'completion_percentage': (completed / total * 100) if total else 0,
            'directions': {},
            'last_updated': self.user_progress['last_updated']
        }
    
    def get_direction_statistics(self) -> Dict:
        directions = {}
        for marker, info in self.markers.items():
            dir_ = info['category']
            if dir_ not in directions:
                directions[dir_] = {'total': 0, 'completed': 0}
            directions[dir_]['total'] += 1
            if self.is_completed(marker):
                directions[dir_]['completed'] += 1
        return directions
    
    def get_next_recommended_markers(self, count: int = 5) -> List[str]:
        available = [m for m in self.markers if not self.is_completed(m)]
        return available[:count]
    
    def get_skill_progress(self, skill: str) -> Dict:
        markers = [m for m, info in self.markers.items() if info['name'].startswith(skill)]
        completed = sum(1 for m in markers if self.is_completed(m))
        return {
            'skill': skill,
            'completed_count': completed,
            'total_count': len(markers),
            'percentage': (completed / len(markers) * 100) if markers else 0,
            'markers': markers
        }
    
    def save_progress(self) -> bool:
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.user_progress, f, indent=2)
            return True
        except:
            return False
    
    def get_completion_timeline(self) -> List[Dict]:
        # Stub
        return [{'marker_id': m, 'completed_at': '2024-01-01', 'skill': 'unknown'} for m in self.user_progress['completed_markers']]
    
    def get_skill_recommendations(self) -> List[Dict]:
        # Stub
        return [{'skill': 'Python', 'reason': 'Next step', 'next_steps': [], 'resources': []}]


