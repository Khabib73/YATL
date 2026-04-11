"""ANSI color codes for terminal output.

Provides constants for colored text using 8-bit ANSI escape sequences.
All sequences are wrapped in `\\x1b[...m` and are safe to use in any terminal
that supports basic colors.
"""

RESET = "\x1b[0m"

BLACK = "\x1b[30m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
MAGENTA = "\x1b[35m"
CYAN = "\x1b[36m"
WHITE = "\x1b[37m"


COLOR_SUCCESS = GREEN
COLOR_SKIPPED = ""  # No color
COLOR_ERROR = RED
COLOR_INFO = ""  # No color
COLOR_HEADER = ""  # No color
COLOR_DIVIDER = ""  # No color


def colorize(text: str, color_code: str) -> str:
    """Wrap text with a color code and reset."""
    if not color_code:
        return text
    return f"{color_code}{text}{RESET}"


def success(text: str) -> str:
    """Color text for successful tests and steps."""
    return colorize(text, COLOR_SUCCESS)


def skipped(text: str) -> str:
    """Color text for skipped tests/steps."""
    return colorize(text, COLOR_SKIPPED)


def error(text: str) -> str:
    """Color text for errors and failures."""
    return colorize(text, COLOR_ERROR)


def info(text: str) -> str:
    """Color text for informational messages."""
    return colorize(text, COLOR_INFO)


def header(text: str) -> str:
    """Color text for headers and dividers."""
    return colorize(text, COLOR_HEADER)
