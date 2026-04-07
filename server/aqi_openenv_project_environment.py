# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
EcoGuard Environment Implementation.

An OpenEnv simulation of a city's Air Quality Index and Operational Efficiency.
"""

import random
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import EcoGuardAction, EcoGuardObservation
except ImportError:
    from models import EcoGuardAction, EcoGuardObservation


class EcoGuardEnvironment(Environment):
    """
    EcoGuard Environment.
    The agent must balance city operational efficiency against rising pollution (AQI).
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        """Initialize the EcoGuard environment."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0
        self._current_aqi = 50.0
        self._city_efficiency = 100.0
        self._wind_speed = 5.0
        self._time_of_day = 0
        self._temperature = 20.0

    def reset(self) -> EcoGuardObservation:
        """
        Reset the environment for a new episode.
        """
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count += 1
        
        self._current_aqi = 50.0
        self._city_efficiency = 100.0
        self._wind_speed = random.uniform(2.0, 10.0)
        self._time_of_day = random.randint(0, 23)
        self._temperature = random.uniform(15.0, 25.0)

        return EcoGuardObservation(
            current_aqi=self._current_aqi,
            city_operational_efficiency=self._city_efficiency,
            wind_speed=self._wind_speed,
            temperature=self._temperature,
            time_of_day=self._time_of_day,
            done=False,
            reward=0.0,
        )

    def step(self, action: EcoGuardAction) -> EcoGuardObservation:  # type: ignore[override]
        """
        Execute a step in the environment.
        """
        self._state.step_count += 1

        # Extract actions and boundaries
        factories = max(0, min(10, action.set_factories_active))
        traffic_pol = max(0, min(2, action.set_traffic_policy))

        # Time progression
        self._time_of_day = (self._time_of_day + 1) % 24
        
        # Weather updates (random walk)
        self._wind_speed = max(0.0, self._wind_speed + random.uniform(-1.0, 1.0))
        # Temperature peaks in the early afternoon
        temp_target = 25.0 if 12 <= self._time_of_day <= 18 else 15.0
        self._temperature += (temp_target - self._temperature) * 0.1 + random.uniform(-0.5, 0.5)

        # Pollution Mechanics
        factory_pollution = factories * 3.0
        
        # Traffic Levels: 0=High(1.0), 1=Medium(0.6), 2=Low(0.2)
        traffic_mult = 1.0
        if traffic_pol == 1:
            traffic_mult = 0.6
        elif traffic_pol == 2:
            traffic_mult = 0.2
            
        traffic_pollution = traffic_mult * 15.0
        
        dispersal = self._wind_speed * 1.5
        
        aqi_delta = factory_pollution + traffic_pollution - dispersal
        self._current_aqi = max(0.0, self._current_aqi + aqi_delta)
        
        # Efficiency Mechanics
        factory_eff = (factories / 10.0) * 60.0  # Up to 60% of city efficiency
        traffic_eff = traffic_mult * 40.0        # Up to 40% of city efficiency
        self._city_efficiency = factory_eff + traffic_eff

        # Reward Calculation
        # Healthy AQI < 100 has no penalty. Penalty kicks in exponentially above 100.
        aqi_penalty = 0.0
        if self._current_aqi > 100:
            excess = self._current_aqi - 100.0
            aqi_penalty = excess * 0.5

        reward = self._city_efficiency - aqi_penalty
        
        # Terminate if AQI exceeds critical threshold
        done = False
        if self._current_aqi > 300.0:
            done = True
            reward -= 500.0  # Huge penalty for failing the city

        # Alternative: max step limit per episode (e.g., 7 days = 168 hours)
        if self._state.step_count >= 168:
            done = True

        return EcoGuardObservation(
            current_aqi=self._current_aqi,
            city_operational_efficiency=self._city_efficiency,
            wind_speed=self._wind_speed,
            temperature=self._temperature,
            time_of_day=self._time_of_day,
            done=done,
            reward=reward,
            metadata={"step": self._state.step_count},
        )

    @property
    def state(self) -> State:
        return self._state
