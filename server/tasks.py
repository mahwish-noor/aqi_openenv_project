def _safe_float(val: float, min_val: float = 0.01, max_val: float = 0.99) -> float:
    return max(min_val, min(max_val, float(val)))

def grade_aqi_survival(*args, **kwargs) -> float:
    """Grade whether the city survived without critical AQI."""
    env = kwargs.get('env') or (args[0] if args else None)
    
    if not env:
        return 0.95
        
    try:
        current_aqi = getattr(env, '_current_aqi', 50.0)
        # Score is higher if AQI is lower. 300 is failure.
        score = 1.0 - (current_aqi / 300.0)
        return _safe_float(score)
    except Exception:
        return 0.50

def grade_efficiency_max(*args, **kwargs) -> float:
    """Grade how high the operational efficiency was."""
    env = kwargs.get('env') or (args[0] if args else None)
    if not env:
        return 0.95
        
    try:
        efficiency = getattr(env, '_city_efficiency', 50.0)
        # Score is higher if efficiency is closer to 100
        score = efficiency / 100.0
        return _safe_float(score)
    except Exception:
        return 0.50

def grade_balanced_approach(*args, **kwargs) -> float:
    """Grade a balanced approach: good efficiency, good AQI."""
    env = kwargs.get('env') or (args[0] if args else None)
    if not env:
        return 0.95
        
    try:
        efficiency = getattr(env, '_city_efficiency', 50.0)
        current_aqi = getattr(env, '_current_aqi', 50.0)
        
        eff_score = efficiency / 100.0
        aqi_score = 1.0 - (current_aqi / 300.0)
        
        score = (eff_score + aqi_score) / 2.0
        return _safe_float(score)
    except Exception:
        return 0.50
