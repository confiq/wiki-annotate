from wiki_annotate.db.file_system import FileSystem, AbstractDB
import logging
import pywikibot
pywikibot.output('init pywikibot & config')  # workaround for https://phabricator.wikimedia.org/T272088


DB_DRIVER: AbstractDB = FileSystem
LOG_DEBUG_LEVEL = logging.DEBUG
CHANCE_SAVE_RANDOM_REVISION = 100
# CPU time for breaking batch process
BRAKE_BATCH_AFTER = 5

logger = logging.getLogger('pywiki')
logger.setLevel(LOG_DEBUG_LEVEL)
logging.basicConfig(level=LOG_DEBUG_LEVEL, format='%(asctime)-15s %(levelno)s %(name)s/%(filename)s:%(lineno)d %(message)s')
