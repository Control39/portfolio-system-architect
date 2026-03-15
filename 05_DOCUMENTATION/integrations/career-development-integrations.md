# Career Development Integrations

## API Endpoints for Integration
- GET /profile - Get user profile
- POST /goals - Add career goal
- PATCH /markers/{id} - Update marker status
- GET /evidence/export - Export evidence package
- GET /skills - List skills
- POST /skills - Add skill
- GET /progress - Get progress percentage

Example from IT-Compass:
```python
import requests
response = requests.get("http://localhost:8000/profile")
profile = response.json()
```

## Data Format
JSON profiles, Pydantic models: UserProfile, Skill, CompetencyMarker (see src/core/models.py).

## Dependencies
- Depends on: IT-Compass (markers), Cloud-Reason (analysis), System-Proof (evidence).
- Depends on Career-Development: Portfolio-Organizer (profile export).

## Integration Examples
Cloud-Reason RAG context injection via gigachain_bridge.py.

