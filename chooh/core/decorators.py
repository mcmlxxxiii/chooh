# -*- coding: utf-8 -*-

import sys
import time
import random
import datetime



task_counter = 0
task_id_prefix = ('%032x' % random.getrandbits(128))[:6]

def log_task(log):
    def decorator(fn):
        def decorated(*args):
            global task_counter
            line = log % args[1:]
            task_counter += 1
            task_id = '%s:%06d' % (task_id_prefix, task_counter)
            sys.stdout.write('%s %s %s\n' %
                    (datetime.datetime.now(), task_id, line))
            start_time = time.time()
            result = fn(*args)
            end_time = time.time()
            sys.stdout.write('%s %s Done in %.04f secs.\n' %
                    (datetime.datetime.now(), task_id, end_time - start_time))
            return result
        return decorated
    return decorator
