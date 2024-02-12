#!/usr/bin/env python3
#
# Dump a C++ file's AST
#

import sys
import clang.cindex

# If clang.cindex cannot locate libclang shared library (so, dylib, dll),
# you may have to give a directory to search here:
# clang.cindex.Config.set_library_path('/path/to/clang-19/lib')

def dumpNode(node, indent=0):
    """ Dump basic node """
    indentation = '  '
    print(f'{indentation*indent}{node.kind}: {node.spelling}: [line={node.location.line}, col={node.location.column}]')
    # Recurse for children of this node
    for n in node.get_children():
        dumpNode(n, indent+1)

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
dumpNode(tu.cursor)

