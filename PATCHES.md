# Local changes on top of upstream BGEN

This repository is a mirror of the upstream BGEN reference implementation,
which lives in a Fossil repository at <https://enkre.net/cgi-bin/code/bgen>.
It vendors **BGEN 1.1.7** (`VERSION` in `wscript`) and carries the changes
below on top of it.

Everything else — `pyproject.toml`, `setup.py`, `MANIFEST.in`, `bgenix/`,
`tests/`, `scripts/`, `AGENTS.md` and `.github/` — is packaging and repository
tooling that upstream does not have, and is not counted as a patch here.

The PyPI version records both parts: `1.1.7.post2` is the second packaging of
upstream 1.1.7.  Bump the `.postN` when this file changes without an upstream
version change.

## Patches

### `src/View.cpp` — use `std::streampos` rather than `std::ios::streampos`

Commit `e327b0a`.

```diff
-std::ios::streampos origin = m_stream->tellg() ;
+std::streampos origin = m_stream->tellg() ;
```

`streampos` was a member typedef of `std::ios_base`, deprecated in C++11 and
removed in C++17, so upstream 1.1.7 does not build with a compiler defaulting
to C++17 or newer. The namespace-scope `std::streampos` from `<iosfwd>` is the
same type and is valid back to C++98.

Not yet submitted upstream.

### Warning fixes

Upstream 1.1.7 emits 45 warnings under `-Wall -pedantic` with GCC 13, 23 of
them in BGEN's own sources. The changes below clear all 23. Each is a change
of type or spelling only: `bgen_to_vcf` produces byte-identical output for all
68 files in `example/` before and after, and the unit tests are unaffected.

* `genfile/include/genfile/bgen/bgen.hpp` — spell the allele count
  `uint32_t( pack.numberOfAlleles )` in the phased-parsing path, matching the
  existing idiom a few lines above. `numberOfAlleles` is a `uint16_t`, so
  `numberOfAlleles - 1` promoted to `int` and was then converted straight back
  to unsigned by the comparison; the cast makes explicit what was already
  happening. Accounts for 18 of the 23 warnings, all from this one site
  instantiated across translation units.
* `src/View.cpp` — compare `m_stream->gcount()` (a signed `std::streamsize`)
  with a `std::size_t` explicitly.
* `apps/bgenix.cpp` — declare `valueSize` as `std::size_t`, since it is only
  ever compared against `std::string::size()`.
* `test/unit/test_variant_data_block.cpp` — catch `BGenError const&` rather
  than by value in `REQUIRE_THROWS_AS`, which was slicing a polymorphic type.

Not yet submitted upstream.

### `3rd_party/*/wscript` — silence warnings from vendored code

boost, sqlite3 and zstd are vendored and not maintained here, so their targets
build with `-w`. This is build configuration rather than a source change, but
it is a deviation from upstream and is recorded for that reason.

The remaining 11 warnings in a clean build come from boost headers included by
BGEN's own translation units, which a flag on the boost target cannot reach;
building those includes with `-isystem` would clear them.
