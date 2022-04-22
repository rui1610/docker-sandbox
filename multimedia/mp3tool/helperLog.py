import logging
import sys

# Custom formatter
class MyFormatterStream(logging.Formatter):

    COLOR_RESET_COLORS = "\033[0;0m"
    COLOR_TIMESTAMP = "\033[38;5;241m"

    COLOR_ERROR = "\033[38;5;160m"
    COLOR_CRITICAL = "\033[38;5;160m"
    COLOR_CHECK = "\033[38;5;10m"
    COLOR_INFO = "\033[38;5;241m"
    COLOR_WARNING = "\033[38;5;11m"

    format_HEADER = COLOR_RESET_COLORS + "#" * 100 + "\n# %(msg)s\n" + "#" * 100 + COLOR_RESET_COLORS
    format_ERROR = COLOR_TIMESTAMP + "[%(asctime)s] " + COLOR_ERROR + "ERROR      : %(msg)s" + COLOR_RESET_COLORS
    #format_ERROR = COLOR_ERROR + "#" * 100 + "\n# ERROR\n" + "#" * 100 + "\n%(msg)s" + COLOR_RESET_COLORS
    format_CHECK = COLOR_TIMESTAMP + "[%(asctime)s] " + COLOR_CHECK + "CHECK      : %(msg)s" + COLOR_RESET_COLORS
    format_INFO = COLOR_TIMESTAMP + "[%(asctime)s] " + COLOR_INFO + "INFO       : %(msg)s" + COLOR_RESET_COLORS
    format_DEBUG = COLOR_TIMESTAMP + "[%(asctime)s] " + COLOR_INFO + "DEBUG       : %(msg)s" + COLOR_RESET_COLORS
    format_WARNING = COLOR_TIMESTAMP + "[%(asctime)s] " + COLOR_WARNING + "WARNING    : %(msg)s" + COLOR_RESET_COLORS
    format_CRITICAL = COLOR_TIMESTAMP + "[%(asctime)s] " + COLOR_CRITICAL + "CRITICAL     : %(msg)s" + COLOR_RESET_COLORS

    def __init__(self):
        super().__init__(fmt=MyFormatterStream.COLOR_TIMESTAMP + "[%(asctime)s] %(msg)s", datefmt="%Y-%m-%d %H:%M:%S", style='%')

    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated

        format_orig = self._style._fmt
        self.datefmt = "%Y-%m-%d %H:%M:%S"

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._style._fmt = MyFormatterStream.format_DEBUG

        if record.levelno == logging.INFO:
            self._style._fmt = MyFormatterStream.format_INFO

        if record.levelno == logging.WARNING:
            self._style._fmt = MyFormatterStream.format_WARNING

        if record.levelno == logging.CRITICAL:
            self._style._fmt = MyFormatterStream.format_CRITICAL

        if record.levelno == logging.ERROR:
            self._style._fmt = MyFormatterStream.format_ERROR

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


def initLogger(debugLevel):
    logging.root.setLevel(debugLevel)

    thisHandler = logging.StreamHandler(sys.stdout)
    thisHandler.setLevel(debugLevel)
    thisHandler.setFormatter(MyFormatterStream())
    logging.root.addHandler(thisHandler)