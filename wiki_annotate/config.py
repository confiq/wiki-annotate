from __future__ import annotations

from wiki_annotate.db.file_system import FileSystem, AbstractDB
from wiki_annotate.db.gcp_storage import GCPStorage
from wiki_annotate.utils import in_container
import logging
import pywikibot
import os

import dotenv

dotenv.load_dotenv()

DB_DRIVER: [AbstractDB | GCPStorage] = GCPStorage if os.getenv('DB_DRIVER') == 'GCPStorage' else FileSystem
CACHE_BUCKET = os.getenv('CACHE_BUCKET')
LOG_DEBUG_LEVEL = logging.DEBUG # TODO: run as info when in serverless
# Negative means to run endlessly
MAX_BATCH_COUNT = os.getenv('MAX_BATCH_COUNT', False)

logger = logging.getLogger('pywiki')
logger.setLevel(LOG_DEBUG_LEVEL)
logging.basicConfig(level=LOG_DEBUG_LEVEL, format='%(asctime)-15s %(levelno)s %(name)s/%(filename)s:%(lineno)d %(message)s')
