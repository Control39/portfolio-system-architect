#!/bin/bash
curl -X POST http://localhost:8000/generate/resume -H "Content-Type: application/json" -d '{"skills": ["python"]}'
