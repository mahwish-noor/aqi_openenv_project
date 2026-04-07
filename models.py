# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the EcoGuard Environment.
"""

from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class EcoGuardAction(Action):
    """Action for the EcoGuard environment - controlling factories and traffic."""

    set_factories_active: int = Field(..., description="Number of factories to run (0 to 10)")
    set_traffic_policy: int = Field(..., description="Traffic policy level (0: Normal/High Traffic, 1: Moderate, 2: Strict/Low Traffic)")


class EcoGuardObservation(Observation):
    """Observation from the EcoGuard environment - current city conditions."""

    current_aqi: float = Field(default=50.0, description="Current Air Quality Index")
    city_operational_efficiency: float = Field(default=100.0, description="City efficiency percentage (0 to 100)")
    wind_speed: float = Field(default=5.0, description="Simulated wind speed in m/s")
    temperature: float = Field(default=22.0, description="Ambient temperature in Celsius")
    time_of_day: int = Field(default=0, description="Hour of the day (0-23)")
