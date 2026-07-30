#!/usr/bin/env python3
"""Report whether upstream BGEN has moved past the version vendored here.

Upstream is a Fossil repository at enkre.net, not GitHub, so there is no
release feed to subscribe to and no tags to watch.  Of the endpoints Fossil
exposes, the tarball rate-limits (HTTP 508) and the timeline RSS feed returns
HTTP 500, but the raw-file endpoint is reliable -- so this reads VERSION
straight out of the release branch's wscript and compares it with ours.

Exit status: 0 in step with upstream, 1 upstream has moved, 2 unreachable.
When run under GitHub Actions it also writes 'status', 'local' and 'upstream'
to $GITHUB_OUTPUT.
"""

import argparse
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

UPSTREAM_WSCRIPT = 'https://enkre.net/cgi-bin/code/bgen/doc/release/wscript'
UPSTREAM_HOME = 'https://enkre.net/cgi-bin/code/bgen'
LOCAL_WSCRIPT = Path(__file__).resolve().parent.parent / 'wscript'

VERSION_PATTERN = re.compile(r'^VERSION\s*=\s*"([^"]+)"', re.MULTILINE)

EXIT_IN_STEP = 0
EXIT_MOVED = 1
EXIT_UNREACHABLE = 2


def parse_version(wscript_text):
    """Pull the VERSION assignment out of a waf wscript."""
    match = VERSION_PATTERN.search(wscript_text)
    if match is None:
        raise ValueError('no VERSION assignment found in wscript')
    return match.group(1)


def fetch_upstream_version(url=UPSTREAM_WSCRIPT, timeout=30):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        body = response.read().decode('utf-8', errors='replace')
    if body.lstrip().startswith('<'):
        # Fossil renders known document types as HTML; only unrecognised
        # files such as wscript come back raw.
        raise ValueError('%s returned HTML rather than the raw file' % url)
    return parse_version(body)


def write_github_output(**values):
    path = os.environ.get('GITHUB_OUTPUT')
    if not path:
        return
    with open(path, 'a', encoding='utf-8') as handle:
        for key, value in values.items():
            handle.write('%s=%s\n' % (key, value))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default=UPSTREAM_WSCRIPT,
                        help='upstream wscript to read (default: %(default)s)')
    parser.add_argument('--timeout', type=float, default=30)
    args = parser.parse_args(argv)

    # Reading our own wscript can fail too, and an uncaught traceback here
    # would exit 1 without writing any output -- which the workflow reads as
    # 'not moved' and passes, leaving the watcher silently doing nothing.
    try:
        local = parse_version(LOCAL_WSCRIPT.read_text())
    except (OSError, ValueError) as error:
        print('Could not read the local version from %s: %s' % (LOCAL_WSCRIPT, error),
              file=sys.stderr)
        write_github_output(status='error', local='', upstream='')
        return EXIT_UNREACHABLE

    try:
        upstream = fetch_upstream_version(args.url, args.timeout)
    except (urllib.error.URLError, ValueError, OSError) as error:
        print('Could not read the upstream version from %s: %s' % (args.url, error),
              file=sys.stderr)
        write_github_output(status='unreachable', local=local, upstream='')
        return EXIT_UNREACHABLE

    if upstream == local:
        print('In step with upstream: BGEN %s.' % local)
        write_github_output(status='in-step', local=local, upstream=upstream)
        return EXIT_IN_STEP

    print('Upstream BGEN is at %s; this tree vendors %s.' % (upstream, local))
    print('Update from %s, then bump VERSION in wscript and version in '
          'pyproject.toml together.' % UPSTREAM_HOME)
    write_github_output(status='moved', local=local, upstream=upstream)
    return EXIT_MOVED


if __name__ == '__main__':
    sys.exit(main())
