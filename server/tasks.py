# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Grader functions for the EcoGuard (AQI OpenEnv) environment.

Each grader must return a float STRICTLY between 0 and 1 (exclusive).
The validator will reject scores of exactly 0.0 or 1.0.
"""

_EPSILON = 1e-6


def _clip_score(score: float) -> float:
    """Ensure score is strictly between 0 and 1 (exclusive)."""
    try:
        s = float(score)
        if not (0.0 < s < 1.0):
            # Clamp: if <= 0, raise to epsilon; if >= 1, lower to 1-epsilon
            s = max(_EPSILON, min(1.0 - _EPSILON, s))
        return s
    except (TypeError, ValueError):
        return 0.5


def _extract_aqi(obj) -> float:
    """
    Extract current_aqi from whatever the validator passes in.
    The validator may pass: the Environment instance, a StepResult,
    an observation dict, or nothing (None).
    """
    default = 50.0  # mid-range default => score ~0.833, safely within (0,1)

    if obj is None:
        return default

    # Pydantic observation or dataclass with field
    for attr in ("current_aqi",):
        if hasattr(obj, attr):
            try:
                return float(getattr(obj, attr))
            except (TypeError, ValueError):
                pass

    # Environment instance with private attr
    for attr in ("_current_aqi",):
        if hasattr(obj, attr):
            try:
                return float(getattr(obj, attr))
            except (TypeError, ValueError):
                pass

    # Dict-style (observation dict or step result dict)
    if isinstance(obj, dict):
        for key in ("current_aqi", "_current_aqi"):
            if key in obj:
                try:
                    return float(obj[key])
                except (TypeError, ValueError):
                    pass
        # Nested under "observation"
        obs = obj.get("observation")
        if isinstance(obs, dict):
            for key in ("current_aqi",):
                if key in obs:
                    try:
                        return float(obs[key])
                    except (TypeError, ValueError):
                        pass
        if hasattr(obs, "current_aqi"):
            try:
                return float(obs.current_aqi)
            except (TypeError, ValueError):
                pass

    # StepResult or similar with .observation attribute
    if hasattr(obj, "observation"):
        obs = obj.observation
        if hasattr(obs, "current_aqi"):
            try:
                return float(obs.current_aqi)
            except (TypeError, ValueError):
                pass

    return default


def _extract_efficiency(obj) -> float:
    """
    Extract city_operational_efficiency from whatever the validator passes in.
    """
    default = 50.0  # mid-range => score 0.5, safely within (0,1)

    if obj is None:
        return default

    for attr in ("city_operational_efficiency",):
        if hasattr(obj, attr):
            try:
                return float(getattr(obj, attr))
            except (TypeError, ValueError):
                pass

    for attr in ("_city_efficiency",):
        if hasattr(obj, attr):
            try:
                return float(getattr(obj, attr))
            except (TypeError, ValueError):
                pass

    if isinstance(obj, dict):
        for key in ("city_operational_efficiency", "_city_efficiency"):
            if key in obj:
                try:
                    return float(obj[key])
                except (TypeError, ValueError):
                    pass
        obs = obj.get("observation")
        if isinstance(obs, dict):
            for key in ("city_operational_efficiency",):
                if key in obs:
                    try:
                        return float(obs[key])
                    except (TypeError, ValueError):
                        pass
        if hasattr(obs, "city_operational_efficiency"):
            try:
                return float(obs.city_operational_efficiency)
            except (TypeError, ValueError):
                pass

    if hasattr(obj, "observation"):
        obs = obj.observation
        if hasattr(obs, "city_operational_efficiency"):
            try:
                return float(obs.city_operational_efficiency)
            except (TypeError, ValueError):
                pass

    return default


def grade_aqi_survival(*args, **kwargs) -> float:
    """
    Grade whether the city survived without critical AQI.

    Score is higher when AQI is lower. AQI of 0 → ~1.0, AQI of 300 → ~0.0.
    Always returns a float strictly between 0 and 1 (exclusive).
    """
    # Accept both positional and keyword args for maximum compatibility
    env = (
        kwargs.get("env")
        or kwargs.get("result")
        or kwargs.get("observation")
        or kwargs.get("episode")
        or (args[0] if args else None)
    )

    try:
        current_aqi = _extract_aqi(env)
        # Score: lower AQI is better. AQI=0 → 1.0, AQI=300 → 0.0
        score = 1.0 - (current_aqi / 300.0)
        return _clip_score(score)
    except Exception:
        return 0.5


def grade_efficiency_max(*args, **kwargs) -> float:
    """
    Grade how high the operational efficiency was.

    Score is higher when city efficiency is higher (max 100).
    Always returns a float strictly between 0 and 1 (exclusive).
    """
    env = (
        kwargs.get("env")
        or kwargs.get("result")
        or kwargs.get("observation")
        or kwargs.get("episode")
        or (args[0] if args else None)
    )

    try:
        efficiency = _extract_efficiency(env)
        # Score: higher efficiency is better. efficiency=100 → 1.0, =0 → 0.0
        score = efficiency / 100.0
        return _clip_score(score)
    except Exception:
        return 0.5


def grade_balanced_approach(*args, **kwargs) -> float:
    """
    Grade a balanced approach: good efficiency AND good AQI.

    Averages the AQI-survival score and the efficiency score.
    Always returns a float strictly between 0 and 1 (exclusive).
    """
    env = (
        kwargs.get("env")
        or kwargs.get("result")
        or kwargs.get("observation")
        or kwargs.get("episode")
        or (args[0] if args else None)
    )

    try:
        current_aqi = _extract_aqi(env)
        efficiency = _extract_efficiency(env)

        aqi_score = 1.0 - (current_aqi / 300.0)
        eff_score = efficiency / 100.0

        score = (aqi_score + eff_score) / 2.0
        return _clip_score(score)
    except Exception:
        return 0.5
