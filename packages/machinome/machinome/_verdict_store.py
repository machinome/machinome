# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The verdict store: decided intersection verdicts kept between runs.

The ADR-070 memo keeps a verdict until the process ends, and the studio
floor starts a fresh `machinome test` for every run, so every floor run
started cold: 1348.9 s for 3DPrintedClocks `wall_clock_02` where the warm
memo answered in 18.35 s (`workflow/warts.md`, 2026-09-29). This module is
the tier beneath that memo (ADR-156). `machinome.test._memoized` consults it
only at an in-process miss, with the run's store switch on and a project
build root to keep it under.

A kept question is identified by STATE, never by location or time: the
SHA-256 of each rigid solid's artifact bytes, a flexible leaf's state
identity, the evaluation path, the placement quantum and ADR-090's
quantised relative placement. That key also carries the STAMP: the store
format, the machinome version, a digest of every Python source of the
running package, the installed versions of the kernels and evaluators on
the verdict path, and the platform; a mesh verdict's key carries as well
the name and version the mesh engine reports of itself. A record kept under
any other stamp is never served, so a framework edit, a kernel upgrade or a
format change starts the store afresh with no maintainer action, and a mesh
engine upgrade starts its mesh verdicts afresh.

The store holds raw engine verdicts -- emptiness, the volume's exact
IEEE-754 bits, and whether the B-rep engine produced it -- and no geometry,
path, name or matrix. The run's volume epsilon is applied after it is
read, exactly as after an in-process hit.

On disk it is a directory, `<build root>/.verdicts`, of immutable,
checksummed SEGMENT files published by atomic rename and merged on read.
Nothing ever modifies a file, so two runs of one project at once need no
lock and lose nothing; a reader that finds a listed segment gone (merged
and deleted by a concurrent compaction, which publishes before it deletes)
lists the directory once more. The store is bounded; when full it evicts
foreign-stamp segments first, then its least recently used records.

The failure direction is a miss. A missing, corrupt, foreign, unreadable or
unwritable store disables this tier for the rest of the process, logged at
debug level, and never raises into an assertion or prints.

Import discipline (design.md §5): at module level this imports cheap
standard-library modules and `machinome._artifact` only. The stamp's
`importlib.metadata`, `importlib.util.find_spec` and `platform` reads and
its walk of the package sources happen inside the stamp function, at the
first store use; no geometry kernel or evaluator is imported at any time.
"""

import atexit
import hashlib
import logging
import os
import re
import struct
import sys
import time

from machinome._artifact import (ArtifactChanged, ArtifactSnapshot,
                                 VERDICT_STORE_DIRECTORY)


logger = logging.getLogger('verdicts')


#: Part of every stamp and every segment header: a change of the record or
#: segment layout starts every store afresh.
FORMAT_VERSION = 1

MAGIC = b'MNVRDCT\x00'

#: magic, format version, the full stamp digest, record count.
HEADER = struct.Struct('<8sI32sQ')

#: key digest, verdict flags, volume bits, last use in whole seconds.
RECORD = struct.Struct('<32sBdQ')

CHECKSUM_SIZE = 32

_EMPTY = 1
_BREP = 2

#: At most this many records across every stamp: about 12 MiB on disk and
#: about 60 MiB of index in memory at the full bound. Internal, in the
#: manner of ADR-092's margins: not a flag and not a variable.
RECORD_LIMIT = 1 << 18

#: A compaction that finds the store over its limit evicts down to this
#: fraction of it.
EVICTION_TARGET = 0.75

#: A load compacts when the current stamp has more segments than this.
SEGMENT_LIMIT = 64

#: Pending records are flushed when a record is queued this many seconds
#: after the last flush, at the end of a `machinome test` run, and at exit.
FLUSH_INTERVAL = 10.0

#: A temporary older than this belongs to a writer that died.
TEMPORARY_AGE = 3600.0

SEGMENT_NAME = re.compile(
    r'^(?P<prefix>[0-9a-f]{16})-[0-9]+-[0-9]+-[0-9a-f]{8}\.seg$')
TEMPORARY_NAME = re.compile(
    r'^\.[0-9a-f]{16}-[0-9]+-[0-9]+-[0-9a-f]{8}\.seg\.tmp$')

#: The distributions whose installed version is part of every stamp, each
#: beside the top-level module it provides: the B-rep path's kernel and its
#: front end, the decoder of the STL a mesh solid is built from, and the
#: flexible evaluator on both paths. The mesh path's engine is not here:
#: a mesh verdict's key carries the identity the mesh engine reports of
#: itself (`persisted_key`'s `engine`), and a B-rep verdict none, so
#: computing the stamp never resolves the mesh engine.
KERNELS = (('cadquery-ocp', 'OCP'), ('cadquery', 'cadquery'),
           ('trimesh', 'trimesh'), ('molejo', 'molejo'))


#: Private counters for tests and probes. Nothing announces them.
counters = dict(served=0, queued=0, touches=0, flushed=0, segments=0,
                loaded=0, compactions=0)


########################################
# Canonical encoding


def _field(data):
    return struct.pack('<Q', len(data)) + data


def _encode(value):
    """A canonical, length-prefixed encoding of nested str/bytes tuples."""
    if isinstance(value, bytes):
        return b'b' + _field(value)
    if isinstance(value, str):
        return b's' + _field(value.encode('utf-8'))
    if isinstance(value, (tuple, list)):
        return (b't' + struct.pack('<Q', len(value))
                + b''.join(_encode(item) for item in value))
    raise TypeError(f'cannot encode {type(value).__name__} in a verdict key')


########################################
# The stamp

_stamp = None


def stamp():
    """The 32-byte stamp of this process, computed once at first use."""
    global _stamp
    if _stamp is None:
        _stamp = _compute_stamp()
    return _stamp


def _compute_stamp():
    import machinome

    parts = [('format', str(FORMAT_VERSION)),
             ('machinome', machinome.__version__),
             ('package', _package_digest())]
    for distribution, module in KERNELS:
        parts.append((distribution, _distribution_token(distribution,
                                                        module)))
    parts.append(('platform', _platform_token()))
    return hashlib.sha256(_encode(parts)).digest()


def _package_digest():
    """Every `.py` file of the running `machinome` package, by
    package-relative path and bytes.

    The whole package rather than a list of the modules on the verdict
    path: a list is a maintenance obligation that fails silently the day
    the next decode, tier or adapter hook lands in a module nobody added.
    """
    import machinome

    package = os.path.dirname(os.path.abspath(machinome.__file__))
    sources = []
    for folder, directories, names in os.walk(package):
        directories[:] = [name for name in directories
                          if name != '__pycache__']
        for name in names:
            if name.endswith('.py'):
                path = os.path.join(folder, name)
                sources.append((os.path.relpath(path, package)
                                .replace(os.sep, '/'), path))
    digest = hashlib.sha256()
    for relative, path in sorted(sources):
        with open(path, 'rb') as handle:
            data = handle.read()
        digest.update(_field(relative.encode('utf-8')))
        digest.update(_field(data))
    return digest.digest()


def _distribution_token(distribution, module):
    """The installed version of `distribution`, read from its metadata --
    never by importing it. Without metadata, the size and mtime of the
    module's origin file if `find_spec` locates it (a conda-built OCP, say),
    else `absent`: an absent module contributes nothing to any verdict."""
    from importlib import metadata

    try:
        return 'version:' + metadata.version(distribution)
    except metadata.PackageNotFoundError:
        pass
    from importlib.util import find_spec

    try:
        spec = find_spec(module)
    except (ImportError, ValueError):
        spec = None
    if spec is None:
        return 'absent'
    origin = getattr(spec, 'origin', None)
    try:
        status = os.stat(origin)
    except (OSError, TypeError):
        return 'located'
    return f'origin:{status.st_size}:{status.st_mtime_ns}'


def _platform_token():
    """What the native kernels were built as."""
    import platform

    return (f'{sys.platform}:{platform.machine()}:'
            f'{sys.implementation.cache_tag}')


########################################
# Keys and digests


def persisted_key(path, quantum, identity1, identity2, placement, engine):
    """The 32-byte digest a verdict is kept under.

    The in-process key's own fields -- evaluation path, quantum and
    placement cells, in its order, so (A, B) and (B, A) stay two
    questions -- with the two identities replaced by persistent ones, the
    stamp added, and `engine`: a tuple of strings naming the engine that
    decided the verdict, `(name, version)` of the mesh engine for a
    mesh verdict and empty for a B-rep one. Nothing else enters it.
    """
    return hashlib.sha256(_encode((
        str(FORMAT_VERSION), stamp(), path, tuple(engine),
        struct.pack('<d', float(quantum)), identity1, identity2,
        bytes(placement)))).digest()


# One digest per artifact observation. Keyed on the FULL observation --
# realpath, device, inode, size, mtime_ns and ctime_ns -- because
# `_atomic_export` stamps every artifact with its source's mtime: a rebuild
# may reproduce the old mtime and size with new bytes, which a
# (path, mtime, size) key would serve the old digest for. The realpath is
# an in-process key only and is never persisted.
_digests = {}


def artifact_digest(path, observation):
    """The SHA-256 of the bytes `observation` names, or None.

    None when the file at `path` no longer is that observation: the
    compared geometry was read from bytes that are not there to digest,
    and filing its verdict under whatever the path holds now could serve
    it for other content.
    """
    cached = _digests.get(observation)
    if cached is not None:
        return cached
    try:
        with ArtifactSnapshot(path) as snapshot:
            if snapshot.observation != observation:
                return None
            data = snapshot.read_bytes()
    except (OSError, ArtifactChanged, ValueError):
        return None
    digest = hashlib.sha256(data).digest()
    for stale in [known for known in _digests
                  if known.realpath == observation.realpath]:
        del _digests[stale]
    _digests[observation] = digest
    return digest


########################################
# Segments


def segment_name(segment_stamp):
    """A fresh segment name, prefixed with the stamp it was written under,
    so a listing tells current segments from foreign ones unopened."""
    return (f'{segment_stamp.hex()[:16]}-{os.getpid()}-{time.time_ns()}-'
            f'{os.urandom(4).hex()}.seg')


def _encode_segment(records, segment_stamp):
    body = bytearray(HEADER.pack(MAGIC, FORMAT_VERSION, segment_stamp,
                                 len(records)))
    for key, is_empty, volume, brep, last_use in records:
        body += RECORD.pack(key, (_EMPTY if is_empty else 0)
                            | (_BREP if brep else 0), volume,
                            int(last_use))
    body += hashlib.sha256(body).digest()
    return bytes(body)


def _decode_segment(data, segment_stamp):
    """The records of a valid segment written under `segment_stamp`, or
    None: wrong magic, version, stamp, length, checksum or flags."""
    if len(data) < HEADER.size + CHECKSUM_SIZE:
        return None
    magic, version, found, count = HEADER.unpack_from(data)
    if (magic != MAGIC or version != FORMAT_VERSION
            or found != segment_stamp
            or len(data) != HEADER.size + count * RECORD.size
            + CHECKSUM_SIZE):
        return None
    body = memoryview(data)[:-CHECKSUM_SIZE]
    if hashlib.sha256(body).digest() != data[-CHECKSUM_SIZE:]:
        return None
    records = []
    for key, flags, volume, last_use in RECORD.iter_unpack(
            body[HEADER.size:]):
        if flags & ~(_EMPTY | _BREP):
            return None
        records.append((key, bool(flags & _EMPTY), volume,
                        bool(flags & _BREP), last_use))
    return records


def write_segment(directory, records, segment_stamp=None):
    """Publish `records` as one new segment in `directory`.

    Written to a temporary beside it and published with `os.replace`,
    atomic on POSIX and Windows: an interrupted write leaves at most an
    unpublished temporary, which nothing reads. Creates the store directory
    itself but never its parent, so a build root that is gone is a failure,
    not a new directory.
    """
    segment_stamp = stamp() if segment_stamp is None else segment_stamp
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass
    name = segment_name(segment_stamp)
    temporary = os.path.join(directory, f'.{name}.tmp')
    path = os.path.join(directory, name)
    try:
        with open(temporary, 'wb') as handle:
            handle.write(_encode_segment(records, segment_stamp))
        os.replace(temporary, path)
    except BaseException:
        try:
            os.remove(temporary)
        except OSError:
            pass
        raise
    return path


def read_segment(path, segment_stamp=None):
    """The records of the segment at `path`, or None if it is missing or
    invalid. Without `segment_stamp`, the one its header names, which its
    name's prefix must agree with."""
    try:
        with open(path, 'rb') as handle:
            data = handle.read()
    except OSError:
        return None
    if segment_stamp is None:
        if len(data) < HEADER.size:
            return None
        segment_stamp = HEADER.unpack_from(data)[2]
        match = SEGMENT_NAME.match(os.path.basename(path))
        if match is None or match.group('prefix') != segment_stamp.hex()[:16]:
            return None
    return _decode_segment(data, segment_stamp)


def _list_directory(directory):
    """The store directory's entries. A seam, so a test can interleave a
    concurrent compaction between a listing and the reads it drives."""
    return os.listdir(directory)


def _record_count(size):
    return max(0, (size - HEADER.size - CHECKSUM_SIZE) // RECORD.size)


########################################
# One project's store


class Store:
    """The store under one build root, as this process sees it."""

    def __init__(self, root):
        self.root = root
        self.directory = os.path.join(root, VERDICT_STORE_DIRECTORY)
        #: key -> (is_empty, volume, brep, last_use)
        self.index = {}
        #: Records to publish at the next flush: new verdicts, and one
        #: touch per key first served from the store in this process.
        self.pending = {}
        self.touched = set()
        self.loaded = False
        #: The failure that disabled this store, or None.
        self.failed = None
        self.last_flush = time.monotonic()

    def _fail(self, error):
        self.failed = error
        self.pending.clear()
        logger.debug('Verdict store under %s disabled: %s', self.root, error)

    # -- reading ------------------------------------------------------------

    def load(self, compact=False):
        """Read and merge every current-stamp segment, once; compact when
        the current stamp has too many segments or the store too many
        records, or when `compact` forces it."""
        if self.loaded:
            return
        self.loaded = True
        try:
            self._load(compact)
        except Exception as error:
            self._fail(error)

    def _read(self, name, current):
        with open(os.path.join(self.directory, name), 'rb') as handle:
            return _decode_segment(handle.read(), current)

    def _load(self, compact):
        current = stamp()
        prefix = current.hex()[:16]
        try:
            names = _list_directory(self.directory)
        except FileNotFoundError:
            return
        read, invalid = {}, set()
        vanished = self._read_listed(names, prefix, current, read, invalid)
        if vanished:
            # Almost always merged and deleted by a concurrent compaction,
            # which published its merged segment first: one more listing
            # holds every record the vanished segments held. A segment that
            # vanishes again is skipped -- misses, never an error.
            names = _list_directory(self.directory)
            self._read_listed(names, prefix, current, read, invalid)

        index = {}
        for records in read.values():
            for key, is_empty, volume, brep, last_use in records:
                known = index.get(key)
                if known is None or last_use > known[3]:
                    index[key] = (is_empty, volume, brep, last_use)
        self.index = index
        counters['loaded'] += len(index)

        foreign = self._foreign_segments(names, prefix)
        total = len(index) + sum(count for _, _, count in foreign)
        if (compact or len(read) + len(invalid) > SEGMENT_LIMIT
                or total > RECORD_LIMIT):
            self._compact(names, read, invalid, foreign, current)

    def _read_listed(self, names, prefix, current, read, invalid):
        vanished = False
        for name in names:
            match = SEGMENT_NAME.match(name)
            if (match is None or match.group('prefix') != prefix
                    or name in read or name in invalid):
                continue
            try:
                records = self._read(name, current)
            except FileNotFoundError:
                vanished = True
                continue
            if records is None:
                invalid.add(name)
            else:
                read[name] = records
        return vanished

    def _foreign_segments(self, names, prefix):
        foreign = []
        for name in names:
            match = SEGMENT_NAME.match(name)
            if match is None or match.group('prefix') == prefix:
                continue
            try:
                status = os.stat(os.path.join(self.directory, name))
            except FileNotFoundError:
                continue
            foreign.append((status.st_mtime_ns, name,
                            _record_count(status.st_size)))
        return foreign

    # -- compaction and eviction -------------------------------------------

    def _compact(self, names, read, invalid, foreign, current):
        """Merge the current stamp's records into one new segment, publish
        it, and only then delete exactly the segments that were merged:
        at every instant each record is in at least one published segment,
        which is what lets a concurrent reader recover by listing again."""
        evicted = []
        total = len(self.index) + sum(count for _, _, count in foreign)
        if total > RECORD_LIMIT:
            target = int(RECORD_LIMIT * EVICTION_TARGET)
            for _, name, count in sorted(foreign):
                if total <= target:
                    break
                evicted.append(name)
                total -= count
            if total > target:
                remaining = total - len(self.index)
                keep = max(0, target - remaining)
                ordered = sorted(self.index.items(),
                                 key=lambda item: item[1][3], reverse=True)
                self.index = dict(ordered[:keep])

        if self.index:
            write_segment(self.directory,
                          [(key, *value) for key, value in self.index.items()],
                          current)
        now = time.time()
        doomed = list(read) + sorted(invalid) + evicted
        for name in names:
            if TEMPORARY_NAME.match(name):
                try:
                    status = os.stat(os.path.join(self.directory, name))
                except FileNotFoundError:
                    continue
                if now - status.st_mtime > TEMPORARY_AGE:
                    doomed.append(name)
        for name in doomed:
            try:
                os.remove(os.path.join(self.directory, name))
            except OSError:
                # Gone already, or open elsewhere (Windows): a later
                # compaction takes it.
                pass
        counters['compactions'] += 1

    # -- serving and keeping -------------------------------------------------

    def lookup(self, key):
        """`(is_empty, volume, brep)` kept under `key`, or None."""
        if not self.loaded:
            self.load()
        if self.failed is not None:
            return None
        found = self.index.get(key)
        if found is None:
            return None
        counters['served'] += 1
        if key not in self.touched:
            # Last use is how eviction knows what a run still asks.
            self.touched.add(key)
            touched = (found[0], found[1], found[2], int(time.time()))
            self.index[key] = touched
            self.pending[key] = touched
            counters['touches'] += 1
            self._flush_if_due()
        return found[:3]

    def record(self, key, is_empty, volume, brep):
        """Keep one newly computed raw verdict."""
        if self.failed is not None:
            return
        value = (bool(is_empty), float(volume), bool(brep),
                 int(time.time()))
        self.index[key] = value
        self.pending[key] = value
        self.touched.add(key)
        counters['queued'] += 1
        self._flush_if_due()

    def _flush_if_due(self):
        if time.monotonic() - self.last_flush >= FLUSH_INTERVAL:
            self.flush()

    def flush(self):
        """Publish the pending records as one segment. Never raises."""
        self.last_flush = time.monotonic()
        if self.failed is not None or not self.pending:
            return
        records = [(key, *value) for key, value in self.pending.items()]
        try:
            write_segment(self.directory, records)
        except Exception as error:
            self._fail(error)
            return
        self.pending.clear()
        counters['flushed'] += len(records)
        counters['segments'] += 1


########################################
# This process's store

_current = None
_disabled = False
_exit_hook = False
_resolved = None

#: A test-harness seam, never set by the product: the framework's own suite
#: suspends the store for the whole session (tests/conftest.py), so a policy
#: a test constructs positionally keeps meaning what its boolean counts
#: assume; the store's own tests lift it on a temporary build root.
_suspended = False


def resolve_root():
    """The build root the store lives under, or None.

    The anchored root under `machinome test` (every declared model of a
    project anchors on the same one), else an absolute `SOLID_BUILD_DIR`,
    else `SOLID_BUILD_DIR` (default `_build`) under the project root found
    above the working directory. Never the builder's bare-relative
    fallback, which would create `_build/` wherever a pytest happens to
    run: with no manifest and nothing anchored there is no store. The root
    must already exist; the store never creates it.
    """
    global _resolved
    builder = sys.modules.get('machinome.core.builder')
    anchored = builder._anchored() if builder is not None else None
    configured = os.environ.get('SOLID_BUILD_DIR', '_build')
    relative = anchored is None and not os.path.isabs(configured)
    signature = (anchored, configured, os.getcwd() if relative else None)
    if _resolved is not None and _resolved[0] == signature:
        return _resolved[1]
    if anchored is not None:
        root = anchored[0]
    elif not relative:
        root = configured
    else:
        from machinome.manifest import ProjectManifestError, project_root

        try:
            root = os.path.join(project_root(), configured)
        except ProjectManifestError:
            root = None
    if root is not None and not os.path.isdir(root):
        root = None
    _resolved = (signature, root)
    return root


def active():
    """This process's store for the current build root, loaded, or None."""
    global _current, _disabled, _exit_hook
    if _suspended or _disabled:
        return None
    try:
        root = resolve_root()
        if root is None:
            return None
        if _current is None or _current.root != root:
            if _current is not None:
                _current.flush()
            _current = Store(root)
            if not _exit_hook:
                atexit.register(flush)
                _exit_hook = True
        _current.load()
    except Exception as error:
        logger.debug('Verdict store disabled: %s', error)
        _disabled = True
        return None
    if _current.failed is not None:
        _disabled = True
        return None
    return _current


def flush():
    """Publish this process's pending records. Never raises."""
    global _disabled
    current = _current
    if current is None:
        return
    current.flush()
    if current.failed is not None:
        _disabled = True


def _reset():
    """Forget everything a new interpreter would not have, without
    flushing: the loaded store and its pending records, the digest memo,
    the stamp, the resolved root and the counters. For tests."""
    global _current, _disabled, _resolved, _stamp
    _current = None
    _disabled = False
    _resolved = None
    _stamp = None
    _digests.clear()
    for name in counters:
        counters[name] = 0
