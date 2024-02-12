#!/usr/bin/env python3
#
# 

import argparse
import json
from clang.cindex import *

# The clang.cindex module needs to find the libclang.so library. On different platforms,
# it may be called libclang.dll or libclang.dylib.
# If the module can't find it, you may need to specify the directory to check:
Config.set_library_path('../../clang-19/lib')

class EnumInfo:
    '''The EnumInfo class just stores information about a single enum value'''
    __slots__ = ['name', 'value', 'file', 'line']

    def __init__(self, name, value, sourcefile, line):
        self.name    = name
        self.value   = value
        self.file    = sourcefile
        self.line    = line

    def toJson(self):
        '''I feel dirty writing this. Json encoding should handle slots.'''
        return {'name':self.name, 'value':self.value, 'file':self.file, 'line':self.line}

class EnumInfoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, EnumInfo):
            return obj.toJson()
        return json.JSONEncoder.default(self, obj)

class EnumIndexer:
    '''
    The EnumIndexer collects enum constant definitions and renders the results
    to C++ source, JSON format, and the console.

    Enum declarations have these working assumptions:
        * The ENUM_DECL's name will be targetEnum
        * The ENUM_DECL must reside in a namespace
        * The ENUM_DECL must have a namespace named targetNamespace as an ancestor

    Matching enums are recorded by their source location, name, and value.
    '''
    def __init__(self, cxxFilename, jsonFilename, targetEnum, targetNamespace):
        self.cxxFilename = cxxFilename
        self.jsonFilename = jsonFilename
        self.targetEnum = targetEnum
        self.targetNamespace = targetNamespace
        self.enums = []   # a list of EnumInfo objects to record enum information
        self.enumIndex = {} # Map FQ enum value to its index in 'enums'

    def renderCxx(self):
        '''Render collected enum metadata to a C++ file.'''
        if not self.cxxFilename:
            return
        with open(self.cxxFilename, 'wt') as cxxFile:
            cxxFile.write('#include <map>\n')
            cxxFile.write('#include <string>\n\n')
            cxxFile.write('class EnumIndex {\n')

            cxxFile.write('    const std::map<std::string, uint32_t> mTlvIdByName = {\n')
            for obj in self.enums:
                cxx = f'        {{"{obj.name}", {obj.value} }}, // {obj.file}:{obj.line}\n'
                cxxFile.write(cxx)
            cxxFile.write('    };\n\n')

            cxxFile.write('    const std::map<uint32_t, std::string> mTlvNameById {\n')
            for value in sorted(self.enumIndex.keys()):
                obj = self.enums[self.enumIndex[value]]
                cxx = f'        {{ {obj.value}, "{obj.name}"}}, // {obj.file}:{obj.line}\n'
                cxxFile.write(cxx)
            cxxFile.write('    };\n\n')
            cxxFile.write('}; // class EnumIndex\n')
        return

    def renderJson(self):
        '''Render the collection of EnumInfo to JSON.'''
        if not self.jsonFilename:
            return
        with open(self.jsonFilename, 'wt') as jsonFile:
            json.dump(self.enums, jsonFile, indent=2, cls=EnumInfoEncoder)
        return

    def renderConsole(self):
        for e in self.enums:
            print(f'{e.value}, {e.name}, {e.file}')

    def recordMatchingEnum(self, node, fqnamespace):
        '''An ENUM_DECL matching the target name was found.
        Save each ENUM_CONSTANT_DECL symbol found into a map.
        '''
        for constant in node.get_children():
            if constant.kind == CursorKind.ENUM_CONSTANT_DECL:
                name = fqnamespace + constant.displayname
                obj = EnumInfo(name, constant.enum_value,  str(constant.location.file),
                               constant.location.line)
                index = len(self.enums)
                self.enums.append(obj)
                self.enumIndex[constant.enum_value] = index
        return

    def handleEnumDecl(self, node, fqnamespace):
        '''
        When an ENUM_DECL is found, perform a few checks to ensure it's one
        to process. The name must match targetEnum, and the parent should be
        a direct namespace, not a class or struct or other enclosing structure
        (functions, too).
        '''
        if node.kind != CursorKind.ENUM_DECL or node.semantic_parent.kind != CursorKind.NAMESPACE:
            return
        # Next, check the enum name matches AND is inside the targetNamespace
        matchingNamespace = '::' + self.targetNamespace + '::'
        if node.spelling == self.targetEnum and matchingNamespace in fqnamespace:
            self.recordMatchingEnum(node, fqnamespace + node.spelling + '::')
        return

    def searchNamespaces(self, node, fqnamespace):
        '''
        Look for namespace nodes and build a fully-qualified name.
        Once an ENUM_DECL is seen, go handle that.
        '''
        if node.kind == CursorKind.ENUM_DECL:
            self.handleEnumDecl(node, fqnamespace)
        else:
            # Search all children of this node
            for c in node.get_children():
                currentNamespace = fqnamespace
                if c.kind == CursorKind.NAMESPACE:
                    currentNamespace += c.spelling + '::'
                self.searchNamespaces(c, currentNamespace)

    def indexFile(self, filename):
        index = Index.create()
        tu = index.parse(filename)
        self.searchNamespaces(tu.cursor, '::')

    def render(self):
        self.renderCxx()
        self.renderJson()
        self.renderConsole()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='index_enums',
        description='Parses C++ sources to index key enum symbols')
    parser.add_argument('filenames', help='File(s) to process', nargs='+')
    parser.add_argument('-e', '--enum', help='The enum{} name',
                        dest='enum', action='store', nargs=1, required=True)
    parser.add_argument('-n', '--namespace', help='Required ancestor namespace',
                        dest='namespace', action='store', nargs=1, required=True)
    parser.add_argument('-j', '--json', help='Generate JSON to filename',
                        dest='jsonFilename', action='store', nargs=1)
    parser.add_argument('-c', '--cpp', help='Generate C++ to filename',
                        dest='cxxFilename', action='store', nargs=1)
    args = parser.parse_args()

    enumIndexer = EnumIndexer(args.cxxFilename[0], args.jsonFilename[0],
                              args.enum[0], args.namespace[0])
    for name in args.filenames:
        enumIndexer.indexFile(name)
    enumIndexer.render()
