# Projekt - System niezawodnego strumieniowania danych po UDP
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 16.01.2023

MAX_CONTENT_LENGTH = 140


def format_data(data: bytes) -> str:
    log_dots = "..." if len(data) > MAX_CONTENT_LENGTH else ""
    return f"{data[:MAX_CONTENT_LENGTH]!r}{log_dots}"
