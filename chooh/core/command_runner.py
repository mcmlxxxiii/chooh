# -*- coding: utf-8 -*-

import os
import sys

from chooh.util.fs import get_dir_hierarchy

from . import convention
from .application import ChoohApplication


def detect_project_root_dir():
    cwd = os.path.normpath(os.getcwdu())
    dir_tree_for_cwd = get_dir_hierarchy(cwd)[::-1]
    root_dir_path = None
    for dir in dir_tree_for_cwd:
        has_app_config = os.path.isfile(
                os.path.join(dir, convention.CONFIG_FNAME))
        if has_app_config:
            root_dir_path = dir
            break
    return root_dir_path


def run(**options):
    root_dir_path = detect_project_root_dir()

    # TODO Check that the root_dir_path is not None.

    # Ensure that the project root is also on PYTHON_PATH.
    sys.path.insert(0, root_dir_path)

    app = ChoohApplication(root_dir_path)

    if options['deploy']:

        if options['<deployment>']:
            app.deploy(options['<deployment>'], auto=options['--auto'])

        elif options['<ddoc>'] and options['<database>']:
            push = {
                    'ddoc': options['<ddoc>'],
                    'target_database': options['<database>']
                }
            app.deploy([push], auto=options['--auto'])
