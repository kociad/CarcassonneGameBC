import logging
from datetime import datetime
import settings

def configureLogging():
    root = logging.getLogger()
    # first, clear out any existing handlers
    for h in root.handlers[:]:
        root.removeHandler(h)

    if settings.DEBUG:
        root.setLevel(logging.DEBUG)
        # file + console as before
        log_filename = datetime.now().strftime("log_%Y-%m-%d_%H-%M-%S.log")
        fh = logging.FileHandler(log_filename, mode='w', encoding='utf-8')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        root.addHandler(fh)
        root.addHandler(ch)
    else:
        root.setLevel(logging.INFO)
        root.addHandler(logging.NullHandler())
