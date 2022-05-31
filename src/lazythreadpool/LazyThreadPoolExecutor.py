from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import logging


class LazyThreadPoolExecutor(ThreadPoolExecutor):

    def __init__(self, max_workers=None,
                    max_pending=1000,
                    max_timeout=None,
                    thread_name_prefix='',
                    initializer=None,
                    initargs=()):

        super().__init__(max_workers=max_workers,
                         thread_name_prefix=thread_name_prefix,
                         initializer=initializer,
                         initargs=initargs)

        self.max_timeout = max_timeout
        self.max_pending=max_pending
        self.futures = set()
        self.logger = logging.getLogger('lazythreadpool')
        self.shutting_down = False


    def _should_block(self):
        exceed_pending = len(self.futures) > self.max_pending
        should_block = exceed_pending and not self.shutting_down
        if should_block:
            self.logger.info('Should block exceed %s (futures %s, max %s), shutting_down %s',
                             exceed_pending, len(self.futures), self.max_pending, self.shutting_down)
        else:
            self.logger.debug('Should not block')

        return should_block


    def drain(self):
        while self._should_block():
            self.logger.debug('Blocking on %s futures, target %s, timeout %s',
                             len(self.futures), self.max_pending, self.max_timeout)
            done, self.futures = wait(self.futures, self.max_timeout, FIRST_COMPLETED)
            self.logger.debug('Done %s, not done %s', len(done), len(self.futures))

    def submit(self, fn, *args, **kwargs):
        f = super().submit(fn, *args, **kwargs)
        self.futures.add(f)
        self.drain()
        return f


    def map(self, func, *iterables, timeout=None, chunksize=1):
        is_done = False
        iterators = []
        futures = set()
        for iterable in iterables:
            iterators.append(iter(iterable))
        while not is_done:
            params = []
            collected = True
            for iterator in iterators:
                try:
                    value = next(iterator)
                except StopIteration:
                    collected = False
                    is_done = True
                    break
                params.append(value)
            if collected:
                future = self.submit(func, *params)
                futures.add(future)
                while len(futures) > self.max_pending:
                    done, futures = wait(futures, None, FIRST_COMPLETED)
                    for f in done:
                        yield f.result()

        while futures:
            done, futures = wait(futures, None, FIRST_COMPLETED)
            for f in done:
                yield f.result()


    def shutdown(self, wait=True):
        self.shutting_down = True
        self.logger.info('Shutting down, wait %s', wait)
        super().shutdown(wait)





