import logging
from wiki_annotate.db.file_system import FileSystem, AbstractDB

log = logging.getLogger(__name__)


DB_DRIVER: AbstractDB = FileSystem
LOG_DEBUG_LEVEL = logging.DEBUG

logging.basicConfig(level=LOG_DEBUG_LEVEL,
                    format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')
