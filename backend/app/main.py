from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.repository import router as repository_router


app = FastAPI(
    title="GitSummarizer API",
    description="Backend API for GitSummarizer",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(repository_router)


@app.get("/")
def root():
    return {"message": "Welcome to GitSummarizer API"}


@app.get("/health")
def health():
    return {"status": "ok"}