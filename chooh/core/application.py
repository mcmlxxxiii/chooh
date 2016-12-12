# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
import couchdbkit
import shutil

from . import convention
from chooh.util import beep
from chooh.util import read_yaml
from chooh.util.fs import copydir
from chooh.util.fs_observer import observe_directory_changes


class ChoohApplication:

    def __init__(self, root_dir):
        #TODO Print an error and exit if root_dir is None.

        self._root_dir = root_dir
        self._ddocs_dir = os.path.join(
                self._root_dir, convention.DDOCS_DIRNAME)
        self._ddocs_assembly_dir = os.path.join(
                self._root_dir, convention.DDOCS_ASSEMBLY_DIRNAME)

        config = read_yaml(os.path.join(self._root_dir,
                                        convention.CONFIG_FNAME))
        if ChoohApplication.validate_config(config):
            self._config = config
        else:
            raise RuntimeError(
                    'There is a problem with %s!' % convention.CONFIG_FNAME)

    @classmethod
    def validate_config(cls, config):
        # TODO
        # - validate presence of `databases` namespace.
        # - validate all of `databases` namespace.
        return True

    def _get_ddoc_names(self):
        ddoc_names = [
               dirname for dirname in os.listdir(self._ddocs_dir)
                   if os.path.isdir(
                       os.path.join(self._ddocs_dir, dirname)) ]
        return ddoc_names

    def _get_ddoc_assembly_dir(self, db_nickname, ddoc_name):
        return os.path.join(self._ddocs_assembly_dir, db_nickname, ddoc_name)

    def _cleanup(self):
        if os.path.exists(self._ddocs_assembly_dir):
            shutil.rmtree(self._ddocs_assembly_dir)

    def _prepare_ddoc_dirs(self, db_nickname, ddoc_name):
        ddocs_assembly_dir = os.path.join(
                self._ddocs_assembly_dir, db_nickname)
        ddoc_assembly_dir = os.path.join(
                self._ddocs_assembly_dir, db_nickname, ddoc_name)

        if os.path.exists(ddoc_assembly_dir):
            shutil.rmtree(ddoc_assembly_dir)

        if not os.path.exists(ddocs_assembly_dir):
            os.makedirs(ddocs_assembly_dir)

        copydir(os.path.join(self._ddocs_dir, ddoc_name),
                ddoc_assembly_dir)

    def _prepare_ddoc(self, db_nickname, ddoc_name):
        ddoc_assembly_dir = os.path.join(
                self._ddocs_assembly_dir, db_nickname, ddoc_name)
        prepare_mod_path = os.path.join(
                self._ddocs_dir, 'prepare_%s.py' % ddoc_name)

        if os.path.isfile(prepare_mod_path):
            try:
                execfile(prepare_mod_path, {
                    'ddoc_dir': ddoc_assembly_dir,
                    'db_nickname': db_nickname
                })
            except Exception as e:
                beep()
                raise e

    def _push_ddoc(self, db_nickname, ddoc_name):
        ddoc_assembly_dir = os.path.join(
                self._ddocs_assembly_dir, db_nickname, ddoc_name)
        server_nickname = self._config['databases'][db_nickname]['server']
        server_uri = self._config['servers'][server_nickname]
        db_name = self._config['databases'][db_nickname]['db_name']
        s = couchdbkit.Server(uri=server_uri)
        db = s.get_or_create_db(db_name)
        ddoc = couchdbkit.designer.document(ddoc_assembly_dir)
        ddoc.push([db], atomic=False)

    def prepare_and_push_one_ddoc(self, db_nickname, ddoc_name):
        sys.stdout.write('%s Pushing ddoc `%s\' to database `%s\'. ' %
                (datetime.datetime.now(), ddoc_name, db_nickname))
        start_time = time.time()
        self._prepare_ddoc_dirs(db_nickname, ddoc_name)
        self._prepare_ddoc(db_nickname, ddoc_name)
        self._push_ddoc(db_nickname, ddoc_name)
        sys.stdout.write(
                'Done (in %.04f secs)\n' % (time.time() - start_time))

    def prepare_and_push_all_ddocs(self, db_nickname):
        self._cleanup()
        for ddoc_name in self._get_ddoc_names():
            self.prepare_and_push_one_ddoc(db_nickname, ddoc_name)

    def auto_push(self, db_nickname, ddoc_name):
        # TODO Determine from changes what ddocs were changed to push only
        # the changed ones.

        if ddoc_name:
            monitored_dir = os.path.join(self._ddocs_dir, ddoc_name)
            def change_handler(events):
                self.prepare_and_push_one_ddoc(db_nickname, ddoc_name)
        else:
            monitored_dir = self._ddocs_dir
            def change_handler(events):
                self.prepare_and_push_all_ddocs(db_nickname)

        observer = observe_directory_changes(monitored_dir, change_handler)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
