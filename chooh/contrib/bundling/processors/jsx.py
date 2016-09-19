# -*- coding: utf-8 -*-


import sys

try:
    from react import jsx
except ImportError:
    print '\nPlease `pip install PyReact` to be able to use jsx bundler ' \
          'include processor.\n'
    sys.exit(1)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


import os



jsx_transformer = jsx.JSXTransformer()

def include_transformed_jsx(tokens, bundle_dir_path):
    if len(tokens) == 1 and tokens[0].endswith('.jsx'):
        relative_file_path = tokens[0]
        jsx_path = os.path.join(bundle_dir_path, relative_file_path)
        block = jsx_transformer.transform(jsx_path)
        return block
