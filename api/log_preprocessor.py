import re


def clean_log(log_text):
    """
    Clean noisy CI/CD logs before TF-IDF processing.
    """

    if log_text is None:
        return ""

    log_text = str(log_text).lower()

    # timestamps
    log_text = re.sub(
        r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}",
        " ",
        log_text
    )

    # urls
    log_text = re.sub(
        r"http[s]?://\S+",
        " ",
        log_text
    )

    # ip addresses
    log_text = re.sub(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        " ",
        log_text
    )

    # linux/windows paths
    log_text = re.sub(
        r"(\/[^\s]+)|([a-zA-Z]:\\[^\s]+)",
        " ",
        log_text
    )

    # hex values
    log_text = re.sub(
        r"0x[a-f0-9]+",
        " ",
        log_text
    )

    # memory addresses
    log_text = re.sub(
        r"<memory at .*?>",
        " <MEMORY_ADDRESS> ",
        log_text
    )

    # long ids
    log_text = re.sub(
        r"\b\d{5,}\b",
        " ",
        log_text
    )

    # keep letters only
    log_text = re.sub(
        r"[^a-z\s]",
        " ",
        log_text
    )

    # remove extra spaces
    log_text = re.sub(
        r"\s+",
        " ",
        log_text
    ).strip()

    return log_text