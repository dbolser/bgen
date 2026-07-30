# Working in this repository

This is a mirror of the upstream BGEN reference implementation, plus the
packaging that publishes its `bgenix` tool to PyPI. Upstream lives in a Fossil
repository at <https://enkre.net/cgi-bin/code/bgen>; see `PATCHES.md` for what
this tree carries on top of it.

## Build

```bash
./waf configure
./waf
```

Outputs land in `build/`. A full build needs a C++11 compiler and zlib headers
(`apt install g++ zlib1g-dev`).

## Tests

Run both suites after changing code.

```bash
./build/test/unit/test_bgen            # C++ unit tests
```

```bash
pip install '.[test]'
pytest                                 # launcher, packaging, bgenix smoke tests
pytest -m slow                         # also builds a wheel and an sdist and
                                       # installs each into a scratch virtualenv
```

A quick end-to-end check of the tool itself:

```bash
./build/apps/bgenix -g example/example.16bits.bgen -list
```

## Layout

| path | what it is |
| --- | --- |
| `src/`, `genfile/`, `db/`, `appcontext/` | the BGEN library (upstream C++) |
| `apps/` | `bgenix`, `cat-bgen`, `edit-bgen` |
| `3rd_party/` | vendored boost, sqlite3 and zstd; their warnings are silenced |
| `bgenix/`, `setup.py`, `pyproject.toml` | the PyPI packaging |
| `tests/` | pytest suite for the packaging layer |
| `scripts/` | the upstream version watcher |

## Conventions

- The C++ sources are indented with **tabs** and follow upstream's spacing
  style (`if( x ) {`, a space before the trailing `;`). Match the file you are
  editing — a patch that converts tabs to spaces turns a one-token change into
  a whole-line diff against upstream.
- Keep changes to the C++ minimal and record each one in `PATCHES.md`, so the
  delta against upstream stays visible.
- The package version is `<upstream BGEN version>.post<packaging revision>`;
  the part before `.post` must match `VERSION` in `wscript`.
