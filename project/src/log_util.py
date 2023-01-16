MAX_CONTENT_LENGTH = 140


def format_data(data: bytes) -> str:
    log_dots = "..." if len(data) > MAX_CONTENT_LENGTH else ""
    return f"{data[:MAX_CONTENT_LENGTH]!r}{log_dots}"
