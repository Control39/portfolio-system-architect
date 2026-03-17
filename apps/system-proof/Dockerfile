FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install chromadb pydantic

EXPOSE 8003

CMD ["python", "proof_schema.py"]
