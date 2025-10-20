from typing import Dict


def simple_risk_model(features: Dict[str, float]) -> float:
    # Placeholder linear combination
    weights = {
        "tvl": 0.0000001,
        "age_days": 0.001,
        "volatility": -0.2,
    }
    score = 0.0
    for key, weight in weights.items():
        score += features.get(key, 0.0) * weight
    # Clamp to [0, 1]
    return max(0.0, min(1.0, 0.5 + score))



