import logging
from datetime import datetime
import settings

def configureLogging():
    root = logging.getLogger()
    
    for h in root.handlers[:]:
        root.removeHandler(h)

    if settings.DEBUG:
        root.setLevel(logging.DEBUG)
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
