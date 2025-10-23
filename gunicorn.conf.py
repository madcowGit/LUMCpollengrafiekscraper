
import multiprocessing

bind = '0.0.0.0:8000'
workers = max(2, multiprocessing.cpu_count() * 2 + 1)
threads = 8
timeout = 60
keepalive = 5
accesslog = '-'  # stdout
errorlog = '-'   # stderr
