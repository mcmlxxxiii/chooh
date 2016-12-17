# -*- coding: utf-8 -*-

import os
import time
import couchdbkit
import shutil
import traceback

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
        self._ddocs_support_dir = os.path.join(
                self._root_dir, convention.DDOCS_SUPPORT_DIRNAME)

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

    def _prepare_ddoc_dirs(self, push_info):
        ddocs_assembly_dir = os.path.join(
                self._ddocs_assembly_dir,
                push_info.deployment)
        ddoc_assembly_dir = os.path.join(
                self._ddocs_assembly_dir,
                push_info.deployment,
                push_info.ddoc)

        if os.path.exists(ddoc_assembly_dir):
            shutil.rmtree(ddoc_assembly_dir)

        if not os.path.exists(ddocs_assembly_dir):
            os.makedirs(ddocs_assembly_dir)

        copydir(os.path.join(self._ddocs_dir, push_info.ddoc),
                ddoc_assembly_dir)

    def _prepare_ddoc(self, push_info, changes, is_continuous):
        ddoc_assembly_dir = os.path.join(
                self._ddocs_assembly_dir, push_info.deployment, push_info.ddoc)
        ddoc_support_dir = os.path.join(
                self._ddocs_support_dir, push_info.deployment, push_info.ddoc)
        if not os.path.exists(ddoc_support_dir):
            os.makedirs(ddoc_support_dir)
        prepare_mod_path = os.path.join(
                self._ddocs_dir, 'prepare_%s.py' % push_info.ddoc)

        if os.path.isfile(prepare_mod_path):
            try:
                context = {
                    'ddoc_assembly_dir': ddoc_assembly_dir,
                    'ddoc_support_dir': ddoc_support_dir,
                    'deployment': push_info.deployment,
                    'is_deployment_continuous': is_continuous,
                    'config': push_info.deployment_config,
                    'changes': changes
                }
                _globals = dict(context)
                _globals.update({ 'context': context })
                execfile(prepare_mod_path, _globals)
            except Exception as e:
                print
                traceback.print_exc()
                beep()
                raise e

    def _push_ddoc(self, push_info):
        ddoc_assembly_dir = os.path.join(
                self._ddocs_assembly_dir,
                push_info.deployment,
                push_info.ddoc)
        server_uri = self._config['servers'][push_info.target_server]
        db_name = push_info.target_database_on_server
        s = couchdbkit.Server(uri=server_uri)
        db = s.get_or_create_db(db_name)
        ddoc = couchdbkit.designer.document(ddoc_assembly_dir)
        ddoc.push([db], atomic=False)

    @log_task('Pushing ddoc <%s> to database <%s>', lambda push_info, *args:
            (push_info.ddoc, push_info.target_database))
    def _prepare_and_push_one_ddoc(self, push_info, changes=None,
            is_continuous=False):
        self._prepare_ddoc_dirs(push_info)
        self._prepare_ddoc(push_info, changes, is_continuous)
        self._push_ddoc(push_info)

    @log_task('Deploying <%s>')
    def _deploy_once(self, deployment_name, is_continuous=False):
        deployment_info = self._get_deployment_info(deployment_name)
        push_list = deployment_info.pushes
        for push_info in push_list:
            self._prepare_and_push_one_ddoc(push_info, is_continuous=is_continuous)

    def _deploy_continiously(self, deployment_name):
        deployment_info = self._get_deployment_info(deployment_name)
        push_list = deployment_info.pushes
        observers = []

        # Making changes relative to monitored directory.
        def process_changes(changes, monitored_dir):
            monitored_dir_len = len(monitored_dir + '/')
            new_changes = {}
            for (group_name, group) in changes.iteritems():
                new_group = []
                for fs_obj in group:
                    if isinstance(fs_obj, list):
                        new_group.append([
                            fs_obj[0][monitored_dir_len:],
                            fs_obj[1][monitored_dir_len:]
                        ])
                    else:
                        new_group.append(fs_obj[monitored_dir_len:])
                new_changes[group_name] = new_group
            return new_changes

        for push_info in push_list:
            monitored_dir = os.path.join(self._ddocs_dir, push_info.ddoc)

            def make_change_handler(push_info, monitored_dir):
                def change_handler(changes):
                    changes = process_changes(changes, monitored_dir)
                    self._prepare_and_push_one_ddoc(
                            push_info,
                            changes=changes,
                            is_continuous=True)
                return change_handler

            observer = observe_directory_changes(
                    monitored_dir,
                    make_change_handler(push_info, monitored_dir))

            observers.append(observer)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            for observer in observers:
                observer.stop()

        for observer in observers:
            observer.join()

    def _get_deployment_info(self, deployment_name):
        return DeploymentInfo(
                    deployment_name,
                    self._config['deployments'][deployment_name])

    def deploy(self, deployment_name, continuously=False):
        if continuously:
            self._deploy_continiously(deployment_name)
        else:
            self._deploy_once(deployment_name, is_continuous=False)



class PushInfo:
    def __init__(self, deployment_name, ddoc, target_database,
            deployment_config):
        self.deployment = deployment_name
        self.ddoc = ddoc
        self.target_database = target_database
        self.deployment_config = deployment_config

        server_name, db_name = target_database.split('/')
        self.target_server = server_name
        self.target_database_on_server = db_name


class DeploymentInfo:
    def __init__(self, deployment_name, deployment_data):
        self.name = deployment_name

        if deployment_data.has_key('config') and \
                isinstance(deployment_data['config'], dict):
            config = dict(deployment_data['config'])
        else:
            config = {}

        self.config = config

        self.pushes = [
                PushInfo(
                    deployment_name,
                    push['ddoc'],
                    push['target_database'],
                    config)
                for push in deployment_data['pushes']
            ]

