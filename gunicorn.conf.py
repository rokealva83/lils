import os
import multiprocessing

BASE_PATH = '/home/lils/'


def path_to(*to):
    return os.path.join(BASE_PATH, *to)


bind = 'unix:' + path_to('tmp', 'gunicorn.sock')

pidfile = path_to('tmp', 'gunicorn.pid')
workers = multiprocessing.cpu_count() * 2 + 1

timeout = 6000

accesslog = path_to('logs', 'gunicorn.access.log')
errorlog = path_to('logs', 'gunicorn.error.log')
loglevel = 'info'
