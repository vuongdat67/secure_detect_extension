"""Convenience entrypoint for running the API with `python -m backend`."""

from backend.api.main import app


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)
