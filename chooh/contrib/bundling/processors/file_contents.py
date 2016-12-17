# -*- coding: utf-8 -*-


import os

from chooh.util.fs import read_file



def include_file_contents(tokens, bundle_dir_path, **kwargs):
    if len(tokens) == 1:
        relative_file_path = tokens[0]
        file_path = os.path.join(bundle_dir_path, relative_file_path)
        block = read_file(file_path)
        return block
