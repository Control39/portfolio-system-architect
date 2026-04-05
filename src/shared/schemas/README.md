# Shared Data Schemas

Centralized Pydantic/SQLAlchemy schema definitions for all apps.

## Structure
```
career.yaml      # UserProfile, Skill, CompetencyMarker
ml-registry.yaml # ModelMetadata, ModelRegistry ops  
proof.yaml       # SystemProof, TraceStep
core.yaml        # PortfolioItem, ADR, common types
```

## Usage
```bash
pip install -r requirements-dev.txt
python tools/generate_pydantic.py career.yaml → src/shared/pydantic/career.py
```

## Validation
```bash
pydanticgen validate *.yaml
```


