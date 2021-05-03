from time import perf_counter
from contextlib import contextmanager
from functools import wraps
from time import time
import logging
import os
import functools
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


def in_container():
    proc_1 = r'/proc/1/sched'

    out = ''
    if os.path.exists(proc_1):
        with open(proc_1, 'r') as fp:
            out = fp.read()

    log.warning(f'content of {proc_1} is: {out}')
    checks = [
        'docker' in out,
        '/lxc/' in out,
        out.split(' ')[0] in ('systemd', 'init'),
        os.path.exists('./dockerenv'),
        os.path.exists('/.dockerinit'),
        os.getenv('container') is not None
    ]
    log.warning(any(checks))
    return any(checks)
