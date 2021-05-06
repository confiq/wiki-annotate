from wiki_annotate.db.file_system import FileSystem, AbstractDB
from wiki_annotate.db.gcp_storage import GCPStorage
from wiki_annotate.utils import in_container
import logging
import pywikibot
pywikibot.output('init pywikibot & config')  # workaround for https://phabricator.wikimedia.org/T272088


DB_DRIVER: AbstractDB = FileSystem
# DB_DRIVER: AbstractDB = GCPStorage
CACHE_BUCKET = 'wiki-cache'
# LOG_DEBUG_LEVEL = logging.INFO if in_container() else logging.DEBUG
LOG_DEBUG_LEVEL = logging.DEBUG
# Should annotation be returned in batches?
MAKE_BATCH_PROCESS = True


logger = logging.getLogger('pywiki')
logger.setLevel(LOG_DEBUG_LEVEL)
logging.basicConfig(level=LOG_DEBUG_LEVEL, format='%(asctime)-15s %(levelno)s %(name)s/%(filename)s:%(lineno)d %(message)s')
