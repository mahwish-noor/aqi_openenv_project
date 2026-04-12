# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
FastAPI application for the Aqi Openenv Project Environment.

This module creates an HTTP server that exposes the AqiOpenenvProjectEnvironment
over HTTP and WebSocket endpoints, compatible with EnvClient.

Endpoints:
    - POST /reset: Reset the environment
    - POST /step: Execute an action
    - GET /state: Get current environment state
    - GET /schema: Get action/observation schemas
    - WS /ws: WebSocket endpoint for persistent sessions

Usage:
    # Development (with auto-reload):
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

    # Production:
    uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 4

    # Or run directly:
    python -m server.app
"""

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:  # pragma: no cover
    raise ImportError(
        "openenv is required for the web interface. Install dependencies with '\n    uv sync\n'"
    ) from e

try:
    from ..models import EcoGuardAction, EcoGuardObservation
    from .aqi_openenv_project_environment import EcoGuardEnvironment
    from .tasks import (
        grade_aqi_survival,
        grade_efficiency_max,
        grade_balanced_approach,
    )
except ImportError:
    from models import EcoGuardAction, EcoGuardObservation  # type: ignore[no-redef]
    from server.aqi_openenv_project_environment import EcoGuardEnvironment  # type: ignore[no-redef]
    from server.tasks import (  # type: ignore[no-redef]
        grade_aqi_survival,
        grade_efficiency_max,
        grade_balanced_approach,
    )

# Task definitions — mirror what openenv.yaml declares so the runtime
# HTTP server can expose task metadata and grading endpoints.
TASKS = [
    {
        "id": "aqi_survival",
        "name": "AQI Survival",
        "description": "Keep the AQI below the critical threshold.",
        "difficulty": "easy",
        "grader": grade_aqi_survival,
    },
    {
        "id": "efficiency_max",
        "name": "Efficiency Maximization",
        "description": "Maximize the city's operational efficiency.",
        "difficulty": "medium",
        "grader": grade_efficiency_max,
    },
    {
        "id": "balanced_approach",
        "name": "Balanced Approach",
        "description": "Balance AQI and efficiency.",
        "difficulty": "hard",
        "grader": grade_balanced_approach,
    },
]


# Create the app with web interface and README integration
app = create_app(
    EcoGuardEnvironment,
    EcoGuardAction,
    EcoGuardObservation,
    env_name="ecoguard",
    max_concurrent_envs=1,  # increase this number to allow more concurrent WebSocket sessions
)


def main(host: str = "0.0.0.0", port: int = 8000):
    """
    Entry point for direct execution via uv run or python -m.

    This function enables running the server without Docker:
        uv run --project . server
        uv run --project . server --port 8001
        python -m aqi_openenv_project.server.app

    Args:
        host: Host address to bind to (default: "0.0.0.0")
        port: Port number to listen on (default: 8000)

    For production deployments, consider using uvicorn directly with
    multiple workers:
        uvicorn aqi_openenv_project.server.app:app --workers 4
    """
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    main()
