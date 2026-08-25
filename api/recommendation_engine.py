def generate_recommendation(
    risk_score,
    prediction,
    failure_type=None,
    raw_log="",
    cleaned_log="",
    tests_failed=0,
    warnings=0,
    actual_result="",
):
    """
    Generate practical CI/CD recommendations based on the risk prediction,
    actual CI result, classified failure type, logs, failed tests and warnings.
    """

    try:
        risk_score = float(risk_score)
    except (TypeError, ValueError):
        risk_score = 0.0

    try:
        tests_failed = int(tests_failed)
    except (TypeError, ValueError):
        tests_failed = 0

    try:
        warnings = int(warnings)
    except (TypeError, ValueError):
        warnings = 0

    prediction = str(prediction).upper() if prediction else "UNKNOWN"
    failure_type = str(failure_type).strip() if failure_type else "Unknown"
    actual_result = str(actual_result or "").strip().upper()


    if actual_result == "PASS":
        if risk_score < 0.40:
            return {
                "recommendation": (
                    "Pipeline risk is low. The run can continue normally."
                ),
                "preventive_advice": (
                    "Continue monitoring warnings, tests, and repository history in future runs."
                ),
                "explanation": (
                    "The real CI run passed and the predicted failure risk is low."
                ),
            }

        if risk_score < 0.70:
            return {
                "recommendation": (
                    "The CI run passed, but DeployPilot detected medium deployment risk. "
                    "Review the size of the change, code-quality warnings, and recent pipeline history before production promotion."
                ),
                "preventive_advice": (
                    "Resolve avoidable warnings, keep changes smaller where practical, and confirm tests and staging checks before release."
                ),
                "explanation": (
                    "The pipeline completed successfully, but Model 1 estimated a medium probability of failure."
                ),
            }

        return {
            "recommendation": (
                "The CI run passed, but DeployPilot detected high predictive risk. "
                "Perform a manual review before production promotion."
            ),
            "preventive_advice": (
                "Review changed files, warnings, resource usage, durations, and recent repository history before continuing."
            ),
            "explanation": (
                "The pipeline completed successfully, but Model 1 estimated high failure risk."
            ),
        }

    if prediction == "PASS" and risk_score < 0.40:
        return {
            "recommendation": (
                "Pipeline risk is low. The run can continue normally."
            ),
            "preventive_advice": (
                "Continue monitoring warnings and test results in future runs."
            ),
            "explanation": (
                "The failure risk score is low and no failure-specific recommendation is required."
            ),
        }

    failure_recommendations = {
        "Test Failure": {
            "recommendation": (
                "Review the failed test cases, check assertion errors, and run the test suite locally before pushing again."
            ),
            "preventive_advice": (
                "Run unit tests locally and make sure new changes do not break existing functionality."
            ),
            "explanation": (
                "The log or prediction indicates that one or more automated tests failed."
            ),
        },
        "Dependency Error": {
            "recommendation": (
                "Check requirements.txt, package-lock.json, dependency versions, and missing packages."
            ),
            "preventive_advice": (
                "Pin dependency versions and verify dependency installation before committing changes."
            ),
            "explanation": (
                "The failure appears related to missing, incompatible, or conflicting dependencies."
            ),
        },
        "Build Failure": {
            "recommendation": (
                "Check syntax errors, build scripts, compiler errors, and missing build artifacts."
            ),
            "preventive_advice": (
                "Run the build command locally before pushing and keep build scripts updated."
            ),
            "explanation": (
                "The pipeline failed during the build stage or while generating build artifacts."
            ),
        },
        "Deployment Failure": {
            "recommendation": (
                "Check deployment target, environment variables, service ports, health checks, and rollback status."
            ),
            "preventive_advice": (
                "Validate deployment configuration in a staging environment before production deployment."
            ),
            "explanation": (
                "The failure appears related to deployment or release execution."
            ),
        },
        "Configuration Error": {
            "recommendation": (
                "Check YAML files, environment variables, configuration values, and indentation errors."
            ),
            "preventive_advice": (
                "Validate configuration files before committing and keep environment-specific settings documented."
            ),
            "explanation": (
                "The pipeline appears to have failed because of invalid or missing configuration."
            ),
        },
        "Permission Error": {
            "recommendation": (
                "Check secrets, access tokens, registry permissions, file permissions, and cloud IAM permissions."
            ),
            "preventive_advice": (
                "Regularly verify CI/CD secrets and permission scopes for deployment and package access."
            ),
            "explanation": (
                "The log indicates that the pipeline does not have enough permission to complete an action."
            ),
        },
        "Network Error": {
            "recommendation": (
                "Check network connectivity, DNS resolution, API endpoints, proxy settings, and runner network access."
            ),
            "preventive_advice": (
                "Use retry logic for temporary network failures and monitor external service availability."
            ),
            "explanation": (
                "The failure appears related to connectivity, DNS, or external service access."
            ),
        },
        "Security Scan Failure": {
            "recommendation": (
                "Review the vulnerability report, upgrade the affected dependency, and re-run the security scan."
            ),
            "preventive_advice": (
                "Run dependency and security checks regularly before merging changes."
            ),
            "explanation": (
                "The pipeline was flagged by a security or vulnerability scanning step."
            ),
        },
        "Resource Exhaustion": {
            "recommendation": (
                "Check memory usage, CPU usage, disk space, build cache, and CI runner resource limits."
            ),
            "preventive_advice": (
                "Optimize heavy jobs, clean unused build artifacts, and monitor runner resource usage."
            ),
            "explanation": (
                "The pipeline likely failed because the runner did not have enough resources."
            ),
        },
        "Timeout": {
            "recommendation": (
                "Check slow tests, long-running jobs, service availability, and timeout settings."
            ),
            "preventive_advice": (
                "Split long jobs, optimize slow tests, and adjust timeout values only when necessary."
            ),
            "explanation": (
                "The pipeline appears to have exceeded the allowed execution time."
            ),
        },
        "Unknown": {
            "recommendation": (
                "Review the cleaned CI/CD log manually and check the failed pipeline stage."
            ),
            "preventive_advice": (
                "Collect more pipeline history so the system can improve future recommendations."
            ),
            "explanation": (
                "The failure type is unknown, so the system provides general debugging guidance."
            ),
        },
    }

    selected = failure_recommendations.get(
        failure_type,
        failure_recommendations["Unknown"],
    )

    recommendation = selected["recommendation"]
    preventive_advice = selected["preventive_advice"]
    explanation = selected["explanation"]

    extra_advice = []

    if risk_score >= 0.70:
        extra_advice.append(
            "This is a high-risk pipeline run. Manual review is recommended before continuing."
        )

    if prediction == "FAIL":
        extra_advice.append(
            "The failure risk model predicts that this pipeline is likely to fail."
        )

    if tests_failed > 0:
        extra_advice.append(
            f"{tests_failed} test(s) failed. Review test output before rerunning the pipeline."
        )

    if warnings > 5:
        extra_advice.append(
            f"{warnings} warning(s) were detected. Review warnings because they may indicate hidden issues."
        )

    if cleaned_log:
        keyword_advice = _get_keyword_based_advice(cleaned_log)
        if keyword_advice:
            extra_advice.append(keyword_advice)

    if extra_advice:
        preventive_advice = preventive_advice + " " + " ".join(extra_advice)

    return {
        "recommendation": recommendation,
        "preventive_advice": preventive_advice,
        "explanation": explanation,
    }


def _get_keyword_based_advice(cleaned_log):
    cleaned_log = cleaned_log.lower()

    if "modulenotfounderror" in cleaned_log or "no module named" in cleaned_log:
        return "The log contains missing module keywords, so dependency files should be checked."

    if "assertionerror" in cleaned_log:
        return "The log contains assertion error keywords, so failed test assertions should be reviewed."

    if "permission denied" in cleaned_log or "secret" in cleaned_log:
        return "The log contains permission or secret keywords, so access credentials should be checked."

    if "timeout" in cleaned_log:
        return "The log contains timeout keywords, so slow jobs or unavailable services should be investigated."

    if "vulnerability" in cleaned_log or "security" in cleaned_log:
        return "The log contains security keywords, so vulnerability scan results should be reviewed."

    if "docker" in cleaned_log and "build" in cleaned_log:
        return "The log contains Docker build keywords, so the Dockerfile and image build context should be checked."

    if "network" in cleaned_log or "dns" in cleaned_log:
        return "The log contains network keywords, so DNS and connectivity should be checked."

    if "memory" in cleaned_log or "cpu" in cleaned_log:
        return "The log contains resource keywords, so runner CPU and memory usage should be checked."

    return ""
