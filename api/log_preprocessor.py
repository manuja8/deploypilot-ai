import re


def clean_log(log_text):
    """
    Clean noisy CI/CD logs.
    """

    if log_text is None:
        return ""

    log_text = str(log_text).lower()

    # Remove timestamps
    log_text = re.sub(
        r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}",
        " ",
        log_text
    )

    # Remove URLs
    log_text = re.sub(
        r"http[s]?://\S+",
        " ",
        log_text
    )

    # Remove IP addresses
    log_text = re.sub(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        " ",
        log_text
    )

    # Remove file paths
    log_text = re.sub(
        r"(\/[^\s]+)|([a-zA-Z]:\\[^\s]+)",
        " ",
        log_text
    )

    # Remove hexadecimal values
    log_text = re.sub(
        r"0x[a-f0-9]+",
        " ",
        log_text
    )

    # Replace memory address text
    log_text = re.sub(
        r"<memory at .*?>",
        " memory_address ",
        log_text
    )

    # Remove long numeric ID
    log_text = re.sub(
        r"\b\d{5,}\b",
        " ",
        log_text
    )

    # Remove remaining numbers
    log_text = re.sub(
        r"\b\d+\b",
        " ",
        log_text
    )

    # Keep letters and spaces only
    log_text = re.sub(
        r"[^a-z\s]",
        " ",
        log_text
    )

    # Remove extra spaces
    log_text = re.sub(
        r"\s+",
        " ",
        log_text
    ).strip()

    return log_text