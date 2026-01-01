"""FastAPI entrypoint for SecureCopilot."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ..config import settings
from ..core.analyzer import CodeAnalyzer
from .schemas import AnalyzeRequest, AnalyzeResponse, build_response


app = FastAPI(
    title="SecureCopilot API",
    description="AI-powered security code review",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Shared analyzer instance (models are lightweight/offline by default)
# NOTE: Heavy model loading is disabled unless SECURECOPILOT_LOAD_MODELS=1
analyzer = CodeAnalyzer(
    str(settings.model_path_asm),
    str(settings.model_path_py),
    load_models=settings.load_models,
)


@app.get("/")
def root():
    return {
        "name": "SecureCopilot API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
def analyze_code(request: AnalyzeRequest):
    supported = {"c", "cpp", "python"}
    if request.language not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Supported: {sorted(supported)}",
        )

    result = analyzer.analyze(
        code=request.code,
        language=request.language,
        file_path=request.file_path,
    )

    return build_response(result)


# For `python -m backend.api.main`
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)
