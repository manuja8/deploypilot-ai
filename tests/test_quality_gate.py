from api.quality_gate import evaluate_quality_gate


test_cases = [
    {
        "name": "LOW risk test",
        "risk_score": 0.20,
        "quality_gate_enabled": True
    },
    {
        "name": "MEDIUM risk test",
        "risk_score": 0.55,
        "quality_gate_enabled": True
    },
    {
        "name": "HIGH risk test with quality gate enabled",
        "risk_score": 0.85,
        "quality_gate_enabled": True
    },
    {
        "name": "HIGH risk test with quality gate disabled",
        "risk_score": 0.85,
        "quality_gate_enabled": False
    },
    {
        "name": "Boundary test at 0.39",
        "risk_score": 0.39,
        "quality_gate_enabled": True
    },
    {
        "name": "Boundary test at 0.40",
        "risk_score": 0.40,
        "quality_gate_enabled": True
    },
    {
        "name": "Boundary test at 0.70",
        "risk_score": 0.70,
        "quality_gate_enabled": True
    }
]


for test_case in test_cases:
    result = evaluate_quality_gate(
        risk_score=test_case["risk_score"],
        quality_gate_enabled=test_case["quality_gate_enabled"]
    )

    print("=" * 70)
    print(test_case["name"])
    print("Risk Score:", result["risk_score"])
    print("Risk Level:", result["risk_level"])
    print("Action:", result["action"])
    print("Quality Gate Enabled:", result["quality_gate_enabled"])
    print("Explanation:", result["threshold_explanation"])
