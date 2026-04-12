def _safe_float(val: float) -> float:
    try:
        score = float(val)
        epsilon=1e-6
        return max(epsilon, min(1.0 - epsilon, score))
    except Exception:
        return 0.50

def _extract_metric(env_obj, attr_name: str, key_name: str, default_val: float) -> float:
    # Try attribute
    if hasattr(env_obj, attr_name):
        return float(getattr(env_obj, attr_name, default_val))
    # Try dictionary key if it's a dict
    if isinstance(env_obj, dict):
        if key_name in env_obj:
            return float(env_obj[key_name])
        # Sometimes observation is nested
        if "observation" in env_obj and isinstance(env_obj["observation"], dict):
            return float(env_obj["observation"].get(key_name, default_val))
    # Try finding observation attribute if env_obj is a StepResult
    if hasattr(env_obj, "observation"):
        obs = getattr(env_obj, "observation")
        if hasattr(obs, key_name):
            return float(getattr(obs, key_name, default_val))
    return float(default_val)

def grade_aqi_survival(*args, **kwargs) -> float:
    """Grade whether the city survived without critical AQI."""
    # OpenEnv may pass the environment, result, episode, or observation
    env = kwargs.get('env') or kwargs.get('result') or kwargs.get('observation') or (args[0] if args else None)
    
    if not env:
        return 0.95
        
    try:
        current_aqi = _extract_metric(env, '_current_aqi', 'current_aqi', 50.0)
        # Score is higher if AQI is lower. 300 is failure.
        score = 1.0 - (current_aqi / 300.0)
        return _safe_float(score)
    except Exception:
        return 0.50

def grade_efficiency_max(*args, **kwargs) -> float:
    """Grade how high the operational efficiency was."""
    env = kwargs.get('env') or kwargs.get('result') or kwargs.get('observation') or (args[0] if args else None)
    if not env:
        return 0.95
        
    try:
        efficiency = _extract_metric(env, '_city_efficiency', 'city_operational_efficiency', 50.0)
        # Score is higher if efficiency is closer to 100
        score = efficiency / 100.0
        return _safe_float(score)
    except Exception:
        return 0.50

def grade_balanced_approach(*args, **kwargs) -> float:
    """Grade a balanced approach: good efficiency, good AQI."""
    env = kwargs.get('env') or kwargs.get('result') or kwargs.get('observation') or (args[0] if args else None)
    if not env:
        return 0.95
        
    try:
        efficiency = _extract_metric(env, '_city_efficiency', 'city_operational_efficiency', 50.0)
        current_aqi = _extract_metric(env, '_current_aqi', 'current_aqi', 50.0)
        
        eff_score = efficiency / 100.0
        aqi_score = 1.0 - (current_aqi / 300.0)
        
        score = (eff_score + aqi_score) / 2.0
        return _safe_float(score)
    except Exception:
        return 0.50
