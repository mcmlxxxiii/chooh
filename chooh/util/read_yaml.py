# -*- coding: utf-8 -*-

import yaml

def read_yaml(yaml_file_path):
    yaml_file = open(yaml_file_path, 'r')
    yaml_data = yaml_file.read()
    yaml_file.close()
    config = yaml.load(yaml_data)
    return config
