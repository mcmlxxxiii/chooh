# -*- coding: utf-8 -*-

import os
import time
import couchdbkit
import shutil

from . import convention
from .decorators import log_task
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

    def _prepare_ddoc(self, db_nickname, ddoc_name, changes):
        ddoc_assembly_dir = os.path.join(
                self._ddocs_assembly_dir, db_nickname, ddoc_name)
        prepare_mod_path = os.path.join(
                self._ddocs_dir, 'prepare_%s.py' % ddoc_name)

        if os.path.isfile(prepare_mod_path):
            try:
                execfile(prepare_mod_path, {
                    'ddoc_dir': ddoc_assembly_dir,
                    'db_nickname': db_nickname,
                    'changes': changes
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

    @log_task('Pushing ddoc <%s> to database <%s>', lambda *args: args[0:2])
    def _prepare_and_push_one_ddoc(self, ddoc_name, db_nickname, changes=None):
        ddoc_dir_path = os.path.join(self._ddocs_dir, ddoc_name)
        self._prepare_ddoc_dirs(db_nickname, ddoc_name)
        self._prepare_ddoc(db_nickname, ddoc_name, changes)
        self._push_ddoc(db_nickname, ddoc_name)

    @log_task('Deploying <%s>')
    def _deploy_once(self, deployment):
        push_list = self._get_deployment_push_list(deployment)
        for push in push_list:
            self._prepare_and_push_one_ddoc(
                    push['ddoc'], push['target_database'])

    def _deploy_continiously(self, deployment):
        push_list = self._get_deployment_push_list(deployment)
        observers = []

        for push in push_list:
            monitored_dir = os.path.join(self._ddocs_dir, push['ddoc'])

            def make_change_handler(ddoc_name, target_database):
                def change_handler(changes):
                    self._prepare_and_push_one_ddoc(
                            ddoc_name, target_database, changes)
                return change_handler

            observer = observe_directory_changes(
                    monitored_dir,
                    make_change_handler(push['ddoc'], push['target_database']))

            observers.append(observer)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            for observer in observers:
                observer.stop()

        for observer in observers:
            observer.join()


    def _get_deployment_push_list(self, deployment):
        if isinstance(deployment, list):
            push_list = deployment
        elif isinstance(deployment, str):
            push_list = self._config['deployments'][deployment]
        else:
            push_list = []
        return push_list

    def deploy(self, deployment, auto=False):
        if auto:
            self._deploy_continiously(deployment)
        else:
            self._deploy_once(deployment)
