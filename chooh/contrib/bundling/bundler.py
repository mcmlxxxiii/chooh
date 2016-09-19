# -*- coding: utf-8 -*-


import os

from chooh.util import beep



class Bundler():

    def __init__(self, **kwargs):
        self._processors = []
        self._formatters = []
        self._includes_start_with = kwargs['includes_start_with']

    def register_processor(self, processor):
        self._processors.append(processor)

    def register_formatter(self, processor):
        self._formatters.append(processor)

    def _process_include(self, *args):
        result = None
        for processor in self._processors:
            result = processor(*args)
            if result:
                break
        return result

    def _format_block(self, included_block, line):
        formatted_block = included_block
        for processor in self._formatters:
            formatted_block = processor(formatted_block, line)
        return formatted_block

    def bundle(self, in_path, out_path):
        bundle_dir_path = os.path.dirname(in_path)
        target_file = open(out_path, 'w+')

        with open(in_path, 'r') as source_file:
            for line in source_file:
                lstripped = line.lstrip()
                block = line
                if lstripped.startswith(self._includes_start_with):
                    tokens = lstripped.rstrip() \
                        [len(self._includes_start_with):].split()
                    included_block = self._process_include(
                            tokens, bundle_dir_path)
                    if included_block:
                        formatted_block = self._format_block(
                                included_block, line)
                        if formatted_block:
                            block = formatted_block
                target_file.write(block)
        target_file.close()
