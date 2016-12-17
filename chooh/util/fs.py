# -*- coding: utf-8 -*-

import os
import shutil, errno


def read_file(file_path):
    f = open(file_path, 'r')
    contents = f.read()
    f.close()
    return contents

#unused
def write_file(file_path, contents):
    f = open(file_path, 'w+')
    f.write(contents)
    f.close()

def copydir(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            raise

def cleanup_dir(dir_path):
    for the_file in os.listdir(dir_path):
        path = os.path.join(dir_path, the_file)
        try:
            if os.path.isfile(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception as e:
            raise e

#unused
def rmdir(dir_path):
    shutil.rmtree(dir_path)

def get_dir_hierarchy(dir_path):
    dir_path_parts = dir_path.split(os.path.sep)
    dir_tree = []
    for i in range(1, len(dir_path_parts)):
        dir_tree.append(os.path.sep.join(dir_path_parts[0:i+1]))
    dir_tree = [ os.path.sep ] + dir_tree
    return dir_tree
