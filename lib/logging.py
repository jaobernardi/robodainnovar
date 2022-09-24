import logging
from colorama import init, Fore, Back
init(autoreset=True)

class ColorFormatter(logging.Formatter):
    # Change this dictionary to suit your coloring needs!
    COLORS = {
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED + Back.WHITE,
        "DEBUG": Fore.YELLOW,
        "INFO": Fore.CYAN,
        "CRITICAL": Fore.WHITE + Back.RED
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        if color:
            record.name = color + record.name
            record.levelname = color + record.levelname
            record.msg = color + record.msg
        return logging.Formatter.format(self, record)


class ColorLogger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name)
        color_formatter = ColorFormatter("%(name)s [%(levelname)s] %(message)s")
        console = logging.StreamHandler()
        console.setFormatter(color_formatter)
        self.addHandler(console)

def setup_logging():
    logging.setLoggerClass(ColorLogger)


def setup_logger(level, filename):
    logging.basicConfig(
        level=level,
        handlers=[
            logging.FileHandler(filename, encoding='utf-8'),
        ]
    )
