# -*- coding: utf-8 -*-


from chooh.util.bundler import Bundler

from chooh.contrib.bundling.processors.file_contents \
        import include_file_contents

from chooh.contrib.bundling.formatters import indent
from chooh.contrib.bundling.formatters import prepend_source_line
from chooh.contrib.bundling.formatters import append_empty_lines



js_bundler = Bundler(includes_start_with='//--')

js_bundler.register_processor(include_file_contents)

js_bundler.register_formatter(indent)
js_bundler.register_formatter(prepend_source_line)
js_bundler.register_formatter(append_empty_lines(2))
