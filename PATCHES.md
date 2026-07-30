# Local changes on top of upstream BGEN

This repository is a mirror of the upstream BGEN reference implementation,
which lives in a Fossil repository at <https://enkre.net/cgi-bin/code/bgen>.
It vendors **BGEN 1.1.7** (`VERSION` in `wscript`) and carries the changes
below on top of it.

Everything else — `pyproject.toml`, `setup.py`, `MANIFEST.in`, `bgenix/`,
`tests/`, `scripts/` and `.github/` — is packaging that upstream does not have,
and is not counted as a patch here.

The PyPI version records both parts: `1.1.7.post1` is the first packaging of
upstream 1.1.7.  Bump the `.postN` when this file changes without an upstream
version change.

## Patches

### `src/View.cpp` — use `std::streampos` rather than `std::ios::streampos`

Commit `e327b0a`.

```diff
-std::ios::streampos origin = m_stream->tellg() ;
+std::streampos origin = m_stream->tellg() ;
```

`streampos` is declared in `<ios>` at namespace scope; it is not a member of
`std::ios`, and stricter compilers reject the qualified form, so upstream 1.1.7
does not build with them.

Not yet submitted upstream.
