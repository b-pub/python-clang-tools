# Python Clang Tools

This repo will contain tools I am experimenting with to manipulate
clang/LLVM's AST. While clang includes a Python wrapper called `clang.cindex`,
it uses the C API and not the AST library with ASTMatchers and so is
limited. However, this is a stable API so tools written like this should
not require updating with each clang version.

The `clang.cindex` package is included in this repo. See the files in
`./clang` for license specifics (Apache 2.0). I am including them here
as a convenience and have not modified them from Clang 19 (commit 2c3ba9f62256,
10-feb-2024).

# Building and Setup

There is nothing to build as the tools and `clang.cindex` are 100% Python.

There may be some setup involved to help the `clang.cindex` code fine the
`libclang.so` (or .dylib, or .dll) on your system. See the top of each tool
script where this function is called:

    clang.cindex.Config.set_library_path('../../clang-19/lib')

# Current Tools

This repo is starting out with two small scripts.
* `dump-ast.py` - Dumps the AST of a translation unit, including the type
  of each node.
* `index_enums.py` - This is an actual tool to extract desired enum values
  defined across multiple sources for indexing

# License

This software is released under the MIT license. See the LICENSE file
for details.

# Example of `index_enums.py`

Example data is provided to see how `index_enums.py` works specifically,
and also to see how a tool like this may be written using the Clang C
API.

```
usage: index_enums [-h] -e ENUM -n NAMESPACE [-j JSONFILENAME] [-c CXXFILENAME]
                   filenames [filenames ...]

Parses C++ sources to index key enum symbols

positional arguments:
  filenames             File(s) to process

optional arguments:
  -h, --help            show this help message and exit
  -e ENUM, --enum ENUM  The enum{} name
  -n NAMESPACE, --namespace NAMESPACE
                        Required ancestor namespace
  -j JSONFILENAME, --json JSONFILENAME
                        Generate JSON to filename
  -c CXXFILENAME, --cpp CXXFILENAME
                        Generate C++ to filename
```

Run the example data with the following shell command. This command instructs
`index_enums` to look for enums named Types, that exist inside a namespace
named "IDs". That namespace does not have to be a direct parent of the enum,
but must be an ancestor (an enclosing namespace).

```bash
$ python3 ./index_enums.py -e Types -n IDs -c enum-index.cpp -j enum-index.json example/test1.cpp
```

This command produces the following output:
```
100, ::person::IDs::Types::NONE, example/test1.cpp
101, ::person::IDs::Types::PERSON_ONE, example/test1.cpp
102, ::person::IDs::Types::PERSON_TWO, example/test1.cpp
103, ::person::IDs::Types::PERSON_THREE, example/test1.cpp
104, ::person::IDs::Types::PERSON_FOUR, example/test1.cpp
200, ::room::IDs::app::Types::NONE, example/test1.cpp
201, ::room::IDs::app::Types::ROOM_ONE, example/test1.cpp
202, ::room::IDs::app::Types::ROOM_TWO, example/test1.cpp
203, ::room::IDs::app::Types::ROOM_THREE, example/test1.cpp
204, ::room::IDs::app::Types::ROOM_FOUR, example/test1.cpp
```

The tool also generates C++ code with this indexing information to
`enum-index.cpp` via the `-c` option. The `-j` option generates JSON
data, in `enum-index.json` for consumption by other tools.

# Author

This code was started 10/Feb/2024.
- Brent Burton
