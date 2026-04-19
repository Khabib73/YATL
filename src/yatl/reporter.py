class Reporter:
    """Simple reporter that collects and prints messages."""

    def __init__(self):
        self.info = []

    def add_info(self, info: str) -> None:
        self.info.append(info)

    def print_info(self) -> None:
        for line in self.info:
            print(line)
        self.info.clear()
