import argparse
import os
import re
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def fail_with_context(message, exc=None):
    print(message, file=sys.stderr)
    if exc is not None:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
    raise SystemExit(1)


def build_failure():
    print("Build release compilation started.")
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "demo.c"
        source.write_text(
            '#include "deploypilot_missing_header.h"\n'
            'int main(void) { return 0; }\n',
            encoding="utf-8",
        )
        result = subprocess.run(
            ["gcc", str(source), "-o", str(Path(tmp) / "demo")],
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        if result.returncode != 0:
            fail_with_context(
                "Build release failed: compiler error; cannot find symbol or required build header. Build terminated with errors."
            )
    fail_with_context("Build scenario unexpectedly succeeded.")


def configuration_error():
    print("Application configuration validation started.")
    os.environ.pop("DEPLOYPILOT_DEMO_SECRET_KEY", None)
    try:
        if not os.getenv("DEPLOYPILOT_DEMO_SECRET_KEY"):
            raise RuntimeError(
                "config yaml validation failed: required environment key SECRET_KEY is missing; "
                "container environment values could not be loaded"
            )
    except RuntimeError as exc:
        fail_with_context("Configuration validation stopped the application.", exc)


def dependency_error():
    print("Dependency install validation started.")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "deploypilot-demo-package-does-not-exist==99.99.99",
            "--disable-pip-version-check",
            "--retries",
            "0",
            "--timeout",
            "5",
        ],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        fail_with_context(
            "Dependency install failed: package fetch failed; failed to select a version for required package; package install could not continue."
        )
    fail_with_context("Dependency scenario unexpectedly succeeded.")


def deployment_failure():
    print("Starting deploy validation.")
    try:
        raise RuntimeError(
            "kubectl deployment health check failed after deploy; target deployment did not become healthy; "
            "rollback release after deploy health check failed"
        )
    except RuntimeError as exc:
        fail_with_context("Deployment rollout validation failed.", exc)


def network_error():
    print("Checking registry network connection.")
    try:
        with socket.create_connection(("127.0.0.1", 1), timeout=1):
            pass
    except OSError as exc:
        fail_with_context(
            "Registry connection failed: connection refused while reading from registry mirror; "
            "unexpected gateway response from registry.",
            exc,
        )
    fail_with_context("Network scenario unexpectedly succeeded.")


def permission_error():
    print("Checking deployment artifact permissions.")
    original_euid = os.geteuid() if hasattr(os, "geteuid") else None
    with tempfile.TemporaryDirectory() as tmp:
        protected = Path(tmp) / "protected"
        protected.mkdir()
        protected.chmod(0o500)
        target = protected / "deployment-artifact.txt"

        try:
            if original_euid == 0 and hasattr(os, "seteuid"):
                os.seteuid(65534)
            target.write_text("demo", encoding="utf-8")
        except OSError as exc:
            fail_with_context(
                "Permission denied while writing deployment artifact; server access is forbidden; "
                "ci deployer cannot modify protected deployment resource.",
                exc,
            )
        finally:
            if original_euid == 0 and hasattr(os, "seteuid"):
                os.seteuid(original_euid)
            protected.chmod(0o700)

    fail_with_context("Permission scenario unexpectedly succeeded.")


def resource_exhaustion():
    print("Starting resource limit validation.")
    import resource

    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        limit = 96 * 1024 * 1024
        new_hard = hard if hard != resource.RLIM_INFINITY and hard < limit else limit
        resource.setrlimit(resource.RLIMIT_AS, (limit, new_hard))
        _ = bytearray(512 * 1024 * 1024)
    except (MemoryError, OSError, ValueError) as exc:
        fail_with_context(
            "Memory limit exceeded: heap space exhausted while processing build output; resource limit reached.",
            exc,
        )
    fail_with_context("Resource exhaustion scenario unexpectedly succeeded.")


def security_scan_failure():
    print("Security scan started.")
    sample = 'DATABASE_URL=db.local\npassword="demo-admin-password"\n'
    if re.search(r"(?i)password\s*=\s*['\"][^'\"]+", sample):
        fail_with_context(
            "Security scan found hardcoded password in configuration; high severity finding detected; "
            "critical vulnerability policy requires remediation before release."
        )
    fail_with_context("Security scan scenario unexpectedly succeeded.")


class DemoCheckoutTests(unittest.TestCase):
    def test_checkout_status(self):
        self.assertEqual(
            "OK",
            "FAIL",
            "expected status OK but got FAIL",
        )


def test_failure():
    print("Running demo application tests.")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DemoCheckoutTests)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    if not result.wasSuccessful():
        fail_with_context(
            "Test stage failed: expected status OK but got FAIL; test error failures detected."
        )
    fail_with_context("Test scenario unexpectedly succeeded.")


def timeout_failure():
    print("Waiting for deployment readiness check.")
    try:
        subprocess.run(
            [sys.executable, "-c", "import time; time.sleep(5)"],
            check=True,
            timeout=1,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired as exc:
        fail_with_context(
            "Process timed out after waiting for service readiness; context deadline exceeded; "
            "timed out waiting for deployment response.",
            exc,
        )
    fail_with_context("Timeout scenario unexpectedly succeeded.")


SCENARIOS = {
    "build_failure": build_failure,
    "configuration_error": configuration_error,
    "dependency_error": dependency_error,
    "deployment_failure": deployment_failure,
    "network_error": network_error,
    "permission_error": permission_error,
    "resource_exhaustion": resource_exhaustion,
    "security_scan_failure": security_scan_failure,
    "test_failure": test_failure,
    "timeout": timeout_failure,
}


def main():
    parser = argparse.ArgumentParser(description="Run one controlled DeployPilot AI CI failure scenario.")
    parser.add_argument("scenario", choices=SCENARIOS.keys())
    args = parser.parse_args()

    print(f"Controlled demo scenario: {args.scenario}")
    SCENARIOS[args.scenario]()


if __name__ == "__main__":
    main()
