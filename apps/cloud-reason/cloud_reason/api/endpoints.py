# components/cloud-reason/api/endpoints.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Cloud-Reason API")
