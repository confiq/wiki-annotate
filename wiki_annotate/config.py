from __future__ import annotations

from wiki_annotate.db.file_system import FileSystem, AbstractDB
from wiki_annotate.db.gcp_storage import GCPStorage
import logging
import os

import dotenv

dotenv.load_dotenv()

DB_DRIVER: [AbstractDB | GCPStorage] = GCPStorage if os.getenv('DB_DRIVER') == 'GCPStorage' else FileSystem
CACHE_BUCKET = os.getenv('CACHE_BUCKET')
LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
# Negative means to run endlessly
MAX_BATCH_COUNT = False if os.getenv('MAX_BATCH_COUNT', 'false') == 'false' else int(os.getenv('MAX_BATCH_COUNT'))
MAX_CPU_TIME = int(os.getenv('MAX_CPU_TIME', '50'))    # seconds of CPU time per load_revisions call
MAX_TOTAL_TIME = int(os.getenv('MAX_TOTAL_TIME', '60'))  # seconds of wall time per load_revisions call
logger = logging.getLogger('pywiki')
logger.setLevel(LOG_LEVEL)
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)-15s %(levelno)s %(name)s/%(filename)s:%(lineno)d %(message)s')
