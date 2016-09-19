# -*- coding: utf-8 -*-


def indent(processed_block, source_line):
    indent = source_line[:-len(source_line.lstrip())]
    if len(indent) > 0:
        processed_block = \
                indent + processed_block.replace('\n', '\n' + indent) + '\n'
    return processed_block


def append_empty_lines(num_lines):
    def real_append_empty_lines(processed_block, source_line):
        return processed_block + num_lines * '\n'
    return real_append_empty_lines


def prepend_source_line(processed_block, source_line):
    return source_line + '\n' + processed_block
