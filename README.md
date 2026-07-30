# BGEN reference implementation

This repository contains a reference implementation of the [BGEN
format](http://www.bgenformat.org), written in C++. The library can be used as the basis for BGEN
support in other software, or as a reference for developers writing their own implementations of
the BGEN format.

### What's included?

This repository contains the library itself, a set of [example data files](/dir?name=example), and a number
of example programs (e.g. [bgen\_to\_vcf](/finfo?name=example/bgen_to_vcf.cpp)) that demonstrate the use of the
library API.

In addition, a number of utilities built using the library are also included in this repository:

* [bgenix](/doc/trunk/doc/wiki/bgenix.md) - a tool to index and efficiently retrieve subsets of a BGEN file. 
* [cat-bgen](/doc/trunk/doc/wiki/cat-bgen.md) - a tool to efficiently concatenate BGEN files.
* [edit-bgen](/doc/trunk/doc/wiki/edit-bgen.md) - a tool to edit BGEN file metadata.
* An R package called [rbgen](/doc/trunk/doc/wiki/rbgen.md) is also constructed in the build directory.
See the [rbgen wiki page](/doc/trunk/doc/wiki/rbgen.md) for more information on using this package.

### Citing BGEN

If you make use of the BGEN library, its tools or example programs, please cite:

Band, G. and Marchini, J., "*BGEN: a binary file format for imputed genotype and haplotype data*",
bioArxiv 308296; doi: <https://doi.org/10.1101/308296>

Thanks!

### License

This BGEN implementation is released under the Boost Software License v1.0. This is a relatively
permissive open-source license that is compatible with many other open-source licenses. See [this
page](http://www.boost.org/users/license.html) and the file
[LICENSE_1_0.txt](/artifact/12bafc460efc829b) for full details.

This repository also contains code from the [sqlite](www.sqlite.org), [boost](www.boost.org), and
[zstandard](http://www.zstd.net) libraries, which comes with their own respective licenses.
(Respectively, [public domain](http://www.sqlite.org/copyright.html), the boost software license,
and the [BSD license](https://github.com/facebook/zstd/blob/dev/LICENSE)). These libraries are not
used in the core BGEN implementation, but are used in the applications, example programs, and
`rbgen` R package.

### Note on UK Biobank data

A particularly important dataset released in BGEN is the imputed genotype data released by the UK
Biobank. See [the relevant wiki page](/wiki/?name=BGEN+in+the+UK+Biobank) for details.

---

# Obtaining and installing BGEN

### In brief

The following commands (typed into a UNIX shell - the dollar symbol indicates the prompt, and shouldn't be typed in)
should perform a basic download and install of the BGEN library, example data and tools:

```bash
# get it
wget http://code.enkre.net/bgen/tarball/release/bgen.tgz
cd bgen
# compile it
./waf configure
./waf
# test it
./build/test/unit/test_bgen
./build/apps/bgenix -g example/example.16bits.bgen -list
```

The following sections contains more information on this process.

### Download

A tarball of the latest release branch is available here: <http://code.enkre.net/bgen/tarball/release>

Alternatively, use [fossil](https://fossil-scm.org) to download the master branch as follows:

```
mkdir bgen
cd bgen
fossil clone https://code.enkre.net/bgen bgen.fossil
fossil open bgen.fossil release
```

(This command can take a while.)

Additionally, pre-built version of the bgen utilities may be available from [this
page](http://www.well.ox.ac.uk/~gav/resources/). **Note**: the recommended use is to download and
compile bgenix for your platform; these binaries are provided for convenience in getting started
quickly.

### Compilation

To compile the code, use the supplied waf build tool:
```
./waf configure
./waf
```
Results will appear under the `build/` directory.  

Note: a full build requires a compiler that supports C++11, e.g. gcc v4.7 or above.  To specify the compiler used, set the `CXX` environment variable during the configure step.  For example (if your shell is `bash`):
```
CXX=/path/to/g++ ./waf configure
./waf
```

The sqlite and zstd libraries are written in C; to specify the C compiler you can additionally add
`CC=/path/to/gcc`. We have tested compilation on gcc 4.9.3 and 5.4.0, and using clang, among others.

If you don't have access to a compiler with C++11 support, you can still build the core bgen
implementation, but won't be able to build the applications or example programs. See [the
wiki](/wiki?name=Troubleshooting_compilation) for more information.

### Testing

BGEN's tests can be run by typing 

```
./build/test/test_bgen
```

or, for more recent versions:

```
./build/test/unit/test_bgen
```

If all goes well a message like `All tests passed` should be printed.

If you have [Robot Test Framework](http://robotframework.org/) installed, you can instead run the
full suite of unit and functional tests like so:

```
./test/functional/run_tests.sh
```

Test results will be placed in the directory `build/test/functional/test-reports`.

### Trying an example

The example program `bgen_to_vcf` reads a bgen file (v1.1 or v1.2) and outputs it as a VCF file to stdout.  You can try running it
by typing

```
./build/example/bgen_to_vcf example/example.8bits.bgen
```

which should output vcf-formatted data to stdout.  We've provided further example bgen files in the `example/` subdirectory.

### Installation

The command

```
./waf install
```

will install the applications listed above into a specified system or user directory.  By default this is `/usr/local`.  To change it, specify the prefix at the configure step:

```
./waf configure --prefix=/path/to/installation/directory
./waf install
```

The programs listed above will be installed into a folder called `bin/` under the prefix dir, e.g.
`bgenix` will be installed as `/path/to/installation/directory/bin/bgenix` etc.

Note that in many cases there's no need for installation; the executables are self-contained. The
install step simply copies them into the destination directory.

(The installation prefix need not be a system-wide directory. For example, I typically specify an
installation directory within my home dir, e.g. `~gav/projects/software/`.

### Branches

This repo follows the branch naming practice in which `release` represents the most up-to-date code
considered in a 'releasable' state. If you are interested in using bgen code in your own project,
we therefore recommend cloning the `release` branch. Code development takes place in the `trunk`
branch and/or in feature branches branched from the `trunk` branch. The command given above
downloads the release branch, which is what most people will want.

### Python package and CI

For people working in pip/uv environments rather than conda, this repository
packages the `bgenix` tool for PyPI.  Installing it compiles bgenix from the
sources in this repository and puts it on your `PATH`:

```
pip install bgenix        # or: uv tool install bgenix
```

This needs a C++ compiler and zlib headers (`apt install g++ zlib1g-dev`), the
same as a plain `./waf` build.  The path to the compiled executable is also
available to Python callers:

```python
from bgenix import bgenix_path
```

Note that this is a packaging shim, not a BGEN library — it gives you the
command-line tool and nothing else.  To read BGEN data in Python use one of the
existing libraries ([`bgen`](https://pypi.org/project/bgen/),
[`bgen-reader`](https://pypi.org/project/bgen-reader/), `cbgen`, `pybgen`), and
note that `bgenix` is also available
[from conda-forge](https://anaconda.org/conda-forge/bgenix).

#### Tests

The C++ unit tests are built by waf and run directly:

```
./waf configure && ./waf && ./build/test/unit/test_bgen
```

The Python layer is covered by pytest:

```
pip install '.[test]'
pytest              # launcher, packaging metadata and bgenix smoke tests
pytest -m slow      # additionally builds a wheel and an sdist, installs each
                    # into a scratch virtualenv and runs bgenix from it
```

#### Continuous integration

`.github/workflows/ci.yml` builds the project, runs both test suites, and
builds and installs the wheel and the sdist.

#### Releasing to PyPI

`.github/workflows/publish.yml` publishes on a `vX.Y.Z` tag.  It publishes the
**sdist only**: the wheel contains a compiled binary, and PyPI does not accept
plain `linux_x86_64` wheels, so binary wheels would have to be built in a
`manylinux` container (e.g. with `cibuildwheel`) first.  The sdist is what
makes `pip install bgenix` compile from source.

Before the first release you need a [PyPI trusted
publisher](https://docs.pypi.org/trusted-publishers/) for this repository and
a `pypi` environment in the repository settings; the upload step fails without
them, so nothing can publish by accident.

The version is `<upstream BGEN version>.post<packaging revision>`, which is the
PEP 440 spelling of Debian's `1.1.7-1` — in fact PEP 440 normalises a literal
`1.1.7-1` to `1.1.7.post1`.  So `bgenix==1.1.7.post1` is the first packaging of
BGEN 1.1.7, and it sorts between `1.1.7` and `1.1.8`.  Bump the `.postN` for a
packaging change or a new local patch; change the part in front of it only when
upstream does.  `tests/test_packaging.py` enforces that the front part matches
`VERSION` in `wscript`.

Note that PyPI rejects PEP 440 *local* versions, so `1.1.7+patch1` is not an
option.  See [PATCHES.md](PATCHES.md) for what this tree carries on top of
upstream.

#### Keeping up with upstream

Upstream BGEN is a [Fossil repository at
enkre.net](https://enkre.net/cgi-bin/code/bgen), not GitHub, so there are no
releases or tags to subscribe to.  `.github/workflows/upstream-check.yml` polls
it weekly instead: it reads `VERSION` out of the release branch's `wscript` and
opens an issue if upstream has moved past the version vendored here.  Run the
same check by hand with:

```
python scripts/check_upstream_version.py
```

Fossil's tarball endpoint rate-limits and its timeline RSS feed is broken, so
the raw-file read is the only reliable signal — the check fails loudly rather
than silently reporting success if that endpoint stops working too.

### More information

See the [source code](/dir?ci=release), 
BGEN [releases](/wiki?name=Releases),
or the [Wiki](/wiki?name=Home) for more information.
