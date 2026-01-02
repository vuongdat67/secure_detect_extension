"""Runtime configuration for SecureCopilot backend."""

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes"}


@dataclass
class Settings:
    # Prefer best-rouge checkpoints as requested
    model_path_asm: Path = MODEL_DIR / "assembly" / "checkpoint-best-rouge"
    model_path_py: Path = MODEL_DIR / "python" / "checkpoint-best-rouge"
    load_models: bool = _env_bool("SECURECOPILOT_LOAD_MODELS", False)


settings = Settings()
