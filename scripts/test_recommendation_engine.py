from api.log_preprocessor import clean_log
from api.recommendation_engine import generate_recommendation


test_cases = [
    {
        "name": "Test Failure recommendation",
        "risk_score": 0.82,
        "prediction": "FAIL",
        "failure_type": "Test Failure",
        "raw_log": "AssertionError expected 200 got 500",
        "tests_failed": 3,
        "warnings": 2
    },
    {
        "name": "Dependency Error recommendation",
        "risk_score": 0.76,
        "prediction": "FAIL",
        "failure_type": "Dependency Error",
        "raw_log": "ModuleNotFoundError: No module named pandas",
        "tests_failed": 0,
        "warnings": 4
    },
    {
        "name": "Deployment Failure recommendation",
        "risk_score": 0.88,
        "prediction": "FAIL",
        "failure_type": "Deployment Failure",
        "raw_log": "Deployment failed. Timeout reached while waiting for service.",
        "tests_failed": 0,
        "warnings": 6
    },
    {
        "name": "Permission Error recommendation",
        "risk_score": 0.74,
        "prediction": "FAIL",
        "failure_type": "Permission Error",
        "raw_log": "Permission denied while reading secret token.",
        "tests_failed": 0,
        "warnings": 1
    },
    {
        "name": "Security Scan Failure recommendation",
        "risk_score": 0.91,
        "prediction": "FAIL",
        "failure_type": "Security Scan Failure",
        "raw_log": "Security scan detected vulnerability CVE-2026-1234",
        "tests_failed": 0,
        "warnings": 8
    },
    {
        "name": "Low Risk PASS recommendation",
        "risk_score": 0.22,
        "prediction": "PASS",
        "failure_type": "Unknown",
        "raw_log": "",
        "tests_failed": 0,
        "warnings": 0
    }
]


for test_case in test_cases:
    cleaned_log = clean_log(test_case["raw_log"])

    result = generate_recommendation(
        risk_score=test_case["risk_score"],
        prediction=test_case["prediction"],
        failure_type=test_case["failure_type"],
        raw_log=test_case["raw_log"],
        cleaned_log=cleaned_log,
        tests_failed=test_case["tests_failed"],
        warnings=test_case["warnings"]
    )

    print("=" * 80)
    print(test_case["name"])
    print("Cleaned Log:", cleaned_log)
    print("Recommendation:", result["recommendation"])
    print("Preventive Advice:", result["preventive_advice"])
    print("Explanation:", result["explanation"])

    #python -m scripts.test_recommendation_engine.py