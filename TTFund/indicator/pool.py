from threading import Thread
from multiprocessing import Pool
from queue import Queue


class ThreadPool:
    def __init__(self, n):
        self.queue = Queue()
        for _ in range(n):
            Thread(target=self.worker, daemon=True).start()

    def worker(self):
        while True:
            func, args, kwargs = self.queue.get()
            func(*args, **kwargs)
            self.queue.task_done()

    def apply_async(self, func, args=None, kwargs=None):
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        self.queue.put((func, args, kwargs))

    def join(self):
        self.queue.join()


class Process:

    def __init__(self, n):
        self.pool = Pool(n)

    def apply_async(self, func, args=tuple()):
        self.pool.apply_async(func, args)

    def close(self):
        self.pool.close()

    def join(self):
        self.close()
        self.pool.join()


def _print():
    print('=========================')


def copy_work():
    a = 0
    while a < 1000000:
        a += 1


if __name__ == '__main__':

    # pool = ThreadPool(10)
    # for i in range(100):
    #     pool.apply_async(_print)
    #
    # pool.join()

    p = Process(15)
    for i in range(1000):
        p.apply_async(copy_work)

    p.join()
