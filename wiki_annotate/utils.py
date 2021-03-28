from time import perf_counter
from contextlib import contextmanager
from functools import wraps
from time import time
import logging

log = logging.getLogger(__name__)


@contextmanager
def catchtime() -> float:
    start = perf_counter()
    yield lambda: perf_counter() - start


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        log.debug('func:%r took: %2.4f sec' % (f.__name__, te-ts))
        return result
    return wrap
