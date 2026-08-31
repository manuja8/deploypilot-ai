def evaluate_quality_gate(
    risk_score,
    quality_gate_enabled=True,
    advisory_reason="",
):

    try:
        risk_score = float(risk_score)
    except (TypeError, ValueError):
        risk_score = 0.0

    risk_score = max(0.0, min(risk_score, 1.0))

    if risk_score <= 0.39:
        risk_level = "LOW"
        action = "ALLOW"
        threshold_explanation = (
            "Risk score is between 0.00 and 0.39. "
            "The pipeline is considered low risk, so it is allowed to continue."
        )

    elif risk_score <= 0.69:
        risk_level = "MEDIUM"
        action = "WARN"
        threshold_explanation = (
            "Risk score is between 0.40 and 0.69. "
            "The pipeline is considered medium risk, so a warning is given but the run is not blocked."
        )

    else:
        risk_level = "HIGH"

        if quality_gate_enabled:
            action = "BLOCK"
            threshold_explanation = (
                "Risk score is between 0.70 and 1.00. "
                "The pipeline is considered high risk, so the quality gate blocks the run."
            )
        else:
            action = "WARN"

            if advisory_reason:
                threshold_explanation = (
                    "Risk score is between 0.70 and 1.00. "
                    "The pipeline is considered high risk, but the quality gate is operating in advisory mode "
                    f"({advisory_reason}), so the ML gate warns instead of blocking."
                )
            else:
                threshold_explanation = (
                    "Risk score is between 0.70 and 1.00. "
                    "The pipeline is considered high risk, but the quality gate is disabled, so only a warning is given."
                )

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "action": action,
        "quality_gate_enabled": quality_gate_enabled,
        "threshold_explanation": threshold_explanation,
    }
