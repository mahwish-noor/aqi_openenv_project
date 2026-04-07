# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""EcoGuard Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import EcoGuardAction, EcoGuardObservation


class EcoGuardEnv(
    EnvClient[EcoGuardAction, EcoGuardObservation, State]
):
    """
    Client for the EcoGuard Environment.
    """

    def _step_payload(self, action: EcoGuardAction) -> Dict:
        """
        Convert EcoGuardAction to JSON payload for step message.
        """
        return {
            "set_factories_active": action.set_factories_active,
            "set_traffic_policy": action.set_traffic_policy,
        }

    def _parse_result(self, payload: Dict) -> StepResult[EcoGuardObservation]:
        """
        Parse server response into StepResult[EcoGuardObservation].
        """
        obs_data = payload.get("observation", {})
        observation = EcoGuardObservation(
            current_aqi=obs_data.get("current_aqi", 50.0),
            city_operational_efficiency=obs_data.get("city_operational_efficiency", 100.0),
            wind_speed=obs_data.get("wind_speed", 5.0),
            temperature=obs_data.get("temperature", 20.0),
            time_of_day=obs_data.get("time_of_day", 0),
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        """
        Parse server response into State object.
        """
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
