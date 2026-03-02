from fastapi import FastAPI

app = FastAPI(title="ML Model Registry API", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "ML Model Registry API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)