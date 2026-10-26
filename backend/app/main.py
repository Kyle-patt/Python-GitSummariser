from fastapi import FastAPI

app = FastAPI(
    title="GitSummarizer API",
    description="API for summarizing GitHub repositories",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "GitSummarizer API"}


@app.get("/health")
def health():
    return {"status": "ok"}