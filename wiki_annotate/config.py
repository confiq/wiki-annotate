import logging
from wiki_annotate.db.file_system import FileSystem, AbstractDB

log = logging.getLogger(__name__)


DB_DRIVER: AbstractDB = FileSystem
LOG_DEBUG_LEVEL = logging.ERROR
CHANCE_SAVE_RANDOM_REVISION = 100


logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')
