from api.log_preprocessor import clean_log


test_logs = [
    """
    2026-07-01 10:44:21
    /home/runner/project/test_login.py
    AssertionError expected 200 got 500
    """,

    """
    ModuleNotFoundError:
    No module named pandas
    Build ID 98234567
    """,

    """
    Deployment failed.
    https://deploy.company.com
    10.20.30.40
    Timeout reached while waiting for service.
    """,

    """
    Permission denied while reading secret.
    Runner path: /home/runner/work/project
    Token ID 99999999
    """,

    """
    Security scan detected vulnerability.
    CVE-2026-1234
    https://security-report.com
    """,

    """
    Docker build failed.
    Dependency conflict detected.
    Permission denied.
    Deployment timeout.
    Security vulnerability found.
    """
]


for index, raw_log in enumerate(test_logs, start=1):
    print("=" * 60)
    print(f"TEST LOG {index}")
    print("RAW LOG:")
    print(raw_log)

    print("CLEANED LOG:")
    print(clean_log(raw_log))

# python -m scripts.test_log_preprocessor