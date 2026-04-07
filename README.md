---
title: EcoGuard Environment Server
emoji: 🏙️
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
---

# EcoGuard Agent Environment

A complex, real-world OpenEnv simulator where an AI agent manages the operational efficiency of an industrial city against its Air Quality Index (AQI). 

The agent's goal is to maintain a healthy AQI while keeping city efficiency as high as possible. If the AQI exceeds a critical threshold, the episode terminates early with a massive penalty.

## Quick Start

The simplest way to use the EcoGuard environment is through the `EcoGuardEnv` class:

```python
from aqi_openenv_project import EcoGuardAction, EcoGuardEnv

try:
    # Create environment from Docker image
    ecoguard_env = EcoGuardEnv.from_docker_image("ecoguard-env:latest")

    # Reset
    result = ecoguard_env.reset()
    print(f"Reset AQI: {result.observation.current_aqi}")

    # Step Example
    action = EcoGuardAction(set_factories_active=5, set_traffic_policy=1)
    result = ecoguard_env.step(action)
    print(f"AQI: {result.observation.current_aqi}")
    print(f"Efficiency: {result.observation.city_operational_efficiency}")
    print(f"Reward: {result.reward}")

finally:
    # Always clean up
    ecoguard_env.close()
```

## Environment Details

### Action
**EcoGuardAction**: Controls factories and traffic.
- `set_factories_active` (int): 0 to 10. Number of factories to keep running.
- `set_traffic_policy` (int): 0 (Normal), 1 (Moderate), 2 (Strict).

### Observation
**EcoGuardObservation**: Returns current conditions.
- `current_aqi` (float): The current AQI value. Normal is < 100. Hazardous is > 300.
- `city_operational_efficiency` (float): Percentage of city operational capacity (0 to 100).
- `wind_speed` (float): Disperses pollution.
- `temperature` (float): Ambient temperature.
- `time_of_day` (int): Hour of the day (0-23).
- `done` (bool): True if AQI exceeds 300, or if episode length exceeds 168 steps (7 days).
- `reward` (float): Based on Efficiency - Penalties(AQI).

### Reward
Calculated as `Reward = city_operational_efficiency - aqi_penalty`.
- `aqi_penalty`: 0 if `current_aqi <= 100`. Exponentially increasing if `current_aqi > 100`.
- Massive penalty (-500) if `current_aqi > 300` and the episode terminates early.

## Local Server

Run the server locally for development:

```bash
uvicorn server.app:app --reload
```
