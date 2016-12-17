# -*- coding: utf-8 -*-

import sys
import time
import random
import datetime



task_counter = 0
task_id_prefix = ('%032x' % random.getrandbits(128))[:6]

def log_task(line_fmt, lmbd = lambda *args: args):
    #TODO Improve the bellow note.
    """ The purpose of the 2nd arg is to slice args of decorated
        to match the correct input for the line_fmt.
    """
    def decorator(fn):
        def decorated(*args, **kwargs):
            global task_counter
            arguments = args[1:]
            arguments = lmbd(*arguments)
            line = line_fmt % arguments
            task_counter += 1
            task_id = '%s-%06d' % (task_id_prefix, task_counter)
            sys.stdout.write('%s %s %s\n' %
                    (datetime.datetime.now(), task_id, line))
            start_time = time.time()
            result = fn(*args, **kwargs)
            end_time = time.time()
            sys.stdout.write('%s %s Done in %.04f secs\n' %
                    (datetime.datetime.now(), task_id, end_time - start_time))
            return result
        return decorated
    return decorator
