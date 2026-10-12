# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The web viewer's still (OpenSpec change `viewer-seam`, capability
`web-snapshot`): the provider `machinome.viewer.web` stages the posed node in
a directory of its own and photographs it in the command's process; the
snapshot command asks it to present inside the build lock, to capture after
the lock is released, and to withdraw afterwards."""

import argparse
import json
import os
import shutil
import tempfile
import unittest
from unittest import TestCase
from unittest.mock import Mock, PropertyMock, patch

from machinome.core.camera import parse_camera
from machinome.viewer import CaptureRequest, ViewerError, viewer
from machinome.viewer.web import stage as stage_module
from machinome.viewer.web.bundle import has_bundle
from machinome.core.builder import prepare_build_dir
from machinome.core.pieces import PieceInventory, fact_sidecar
from machinome import currency
from machinome.manager.snapshot import Snapshot
from tests.test_build_lock import lock_is_held
from tests.test_export import Cube

web = viewer('web')

needs_viewer = unittest.skipUnless(
    has_bundle(), 'machinome-viewer not installed (pip install "machinome[viewer]")'
)


def snapshot_args(**overrides):
    values = dict(path='model.py', output='shot.png', time=0.0, camera=None,
                  autocenter=False, viewall=False, imgsize='100x100',
                  projection=None, colorscheme=None, render=False,
                  preview=False, view=None, viewer='web')
    values.update(overrides)
    return argparse.Namespace(**values)


def web_snapshot(node, build_dir, args):
    """`machinome snapshot --viewer web` on `node`, built in `build_dir`."""
    snapshot = Snapshot()
    with patch('machinome.manager.snapshot.select_model') as selected, \
         patch('machinome.manager.snapshot.load_node', return_value=node), \
         patch('machinome.manager.snapshot.get_build_dir',
               return_value=build_dir):
        selected.return_value.reference = 'model.py'
        snapshot.handle(args)
    return snapshot


@needs_viewer
class BrowserStagingTest(TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.build_dir = os.path.join(self.temporary.name, "_build")
        os.makedirs(self.build_dir)
        self.node = Cube(self.build_dir)
        self.model = self.node.stl_file

    def test_stage_copies_every_artifact_from_its_pinned_identity(self):
        staging = stage_module.stage(self.node, self.build_dir)
        self.addCleanup(web.withdraw, staging)
        staged_model = os.path.join(staging, "parts", "cube.stl")
        with open(self.model, 'rb') as source, open(staged_model, 'rb') as copy:
            self.assertEqual(source.read(), copy.read())
        self.assertNotEqual(os.stat(self.model).st_ino,
                            os.stat(staged_model).st_ino)
        os.remove(self.model)
        with open(staged_model, "rb") as staged:
            self.assertIn(b"solid cube", staged.read())

    def test_stage_holds_the_document_and_nothing_of_the_viewer(self):
        staging = stage_module.stage(self.node, self.build_dir)
        self.addCleanup(web.withdraw, staging)
        self.assertEqual(sorted(os.listdir(staging)), ['parts', 'viewer.json'])

    def test_stage_does_not_create_a_fact_record_in_the_build(self):
        record = fact_sidecar(self.model)
        self.assertFalse(os.path.exists(record))
        staging = stage_module.stage(self.node, self.build_dir)
        self.addCleanup(web.withdraw, staging)
        self.assertFalse(os.path.exists(record))

    def test_stage_does_not_restamp_metadata_only_stale_currency(self):
        """The snapshot read path must not invoke currency's mutating
        equal-content fallback when source metadata no longer settles."""
        with PieceInventory() as inventory:
            inventory.register(self.node, 'parts/cube.stl')
        fact = fact_sidecar(self.model)
        currency.record(self.model, 'd' * 64, 'f' * 64)
        source_record = currency.sidecar(self.model)

        def state(path):
            stat = os.stat(path)
            with open(path, 'rb') as stream:
                return stream.read(), stat.st_mtime_ns, stat.st_ctime_ns

        before = {path: state(path)
                  for path in (self.model, fact, source_record)}
        stale_mtime = os.stat(self.model).st_mtime_ns + 1
        with (patch.object(type(self.node), 'mtime_ns',
                           new_callable=PropertyMock,
                           return_value=stale_mtime),
              patch.object(self.node, '_up_to_date',
                           side_effect=AssertionError(
                               'read-only staging called mutating currency'))):
            staging = stage_module.stage(self.node, self.build_dir)
        self.addCleanup(web.withdraw, staging)

        self.assertEqual(
            {path: state(path) for path in (self.model, fact, source_record)},
            before)

    def test_capture_begins_after_the_build_lock_is_released(self):
        node = self.node
        observed = {}
        with (
            patch.object(node, "build_stls") as build,
            patch.object(node, "set_keyframe"),
            patch("machinome.viewer.web.capture") as capture,
        ):
            build.side_effect = lambda: observed.update(
                building=lock_is_held(self.build_dir))
            capture.side_effect = lambda *args: observed.update(
                capturing=lock_is_held(self.build_dir))
            web_snapshot(node, self.build_dir, snapshot_args())
        self.assertEqual(observed, {'building': True, 'capturing': False})

    def test_stage_is_removed_when_capture_fails(self):
        node = self.node
        with (
            patch.object(node, "build_stls"),
            patch.object(node, "set_keyframe"),
            patch("machinome.viewer.web.capture",
                  side_effect=ViewerError("boom")),
            patch("sys.stderr"),
        ):
            with self.assertRaises(SystemExit) as raised:
                web_snapshot(node, self.build_dir, snapshot_args())
        self.assertEqual(raised.exception.code, 1)
        leftovers = [name for name in os.listdir(self.temporary.name)
                     if name.startswith("_build.web-snapshot.")]
        self.assertEqual(leftovers, [])

    def test_the_staged_document_carries_no_bindings_key(self):
        """The web-snapshot document is keyframed and numeric by
        construction (design.md D6-D7, tasks.md 3.1): `stage()` never
        calls `bind_document`, so it can never carry a `bindings` key or
        declare version 4 -- asserted here, not built, since nothing
        about this path changed."""
        staging = stage_module.stage(self.node, self.build_dir)
        self.addCleanup(web.withdraw, staging)
        with open(os.path.join(staging, 'viewer.json')) as handle:
            document = json.load(handle)

        self.assertNotIn('bindings', document)
        self.assertIn(document['version'], (2, 3))

    def test_stage_survives_overlapping_build_preparation(self):
        staging = stage_module.stage(self.node, self.build_dir)
        self.addCleanup(web.withdraw, staging)
        staged_document = os.path.join(staging, 'viewer.json')
        staged_model = os.path.join(staging, 'parts', 'cube.stl')

        prepare_build_dir(self.build_dir)

        self.assertTrue(os.path.isfile(staged_document))
        with open(staged_model, 'rb') as artifact:
            self.assertIn(b'solid cube', artifact.read())


@needs_viewer
class PublishedBuildIsNotDisturbedTest(TestCase):
    """A snapshot is a reader: it must not republish or sweep the build."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.build_dir = os.path.join(self.temporary.name, "_build")
        os.makedirs(os.path.join(self.build_dir, "parts"))
        self.unrelated = os.path.join(self.build_dir, "parts", "other.stl")
        with open(self.unrelated, "wb") as output:
            output.write(b"solid other\nendsolid other\n")
        self.document = os.path.join(self.build_dir, "viewer.json")
        with open(self.document, "w") as output:
            json.dump({
                "format": "machinome-document", "version": 1,
                "animation": {"fps": 30, "frames": 360},
                "root": {"name": "other", "type": "rigid",
                         "model": "parts/other.stl", "children": []},
            }, output)
        self.errors = os.path.join(self.build_dir, "errors.json")
        with open(self.errors, "w") as output:
            json.dump({"error": "a real failure", "tstamp": 1.0}, output)

    def render(self):
        node = Cube(self.build_dir)
        with (
            patch.object(node, "build_stls"),
            patch.object(node, "set_keyframe"),
            patch("machinome.viewer.web.capture") as capture,
        ):
            capture.side_effect = lambda staging, *rest: self.assertTrue(
                os.path.isfile(os.path.join(staging, "viewer.json")))
            web_snapshot(node, self.build_dir, snapshot_args(
                output=os.path.join(self.temporary.name, "shot.png")))

    def test_artifacts_of_another_published_tree_survive(self):
        self.render()
        self.assertTrue(os.path.isfile(self.unrelated))

    def test_the_published_document_is_left_alone(self):
        with open(self.document) as source:
            before = source.read()
        self.render()
        with open(self.document) as source:
            self.assertEqual(source.read(), before)

    def test_a_recorded_build_error_is_not_cleared(self):
        self.render()
        self.assertTrue(os.path.isfile(self.errors))

    def test_the_staged_document_describes_the_photographed_node(self):
        staged = {}
        original = stage_module.stage

        def capture_stage(node, build_dir):
            staging = original(node, build_dir)
            with open(os.path.join(staging, "viewer.json")) as source:
                staged.update(json.load(source))
            return staging

        with patch.object(stage_module, "stage", side_effect=capture_stage):
            self.render()
        self.assertEqual(staged["root"]["name"], "Cube")
        self.assertEqual(staged["root"]["model"], "parts/cube.stl")


class CaptureInProcessTest(TestCase):
    """The photograph is the web viewer's, taken in the command's process
    (`viewer-seam`, ADR-194): the provider resolves the camera notation,
    mounts the staged directory and photographs it, and runs no program of
    the viewer's."""

    def captured(self, request, output='shot.png'):
        with patch('machinome.viewer.web.capture.Capture') as capture:
            web.capture('/tmp/staged', request, output)
        capture.assert_called_once_with('/tmp/staged')
        rendered = capture.return_value.render
        rendered.assert_called_once()
        return rendered.call_args.args

    def test_the_staging_directory_is_photographed_at_its_size_and_time(self):
        output, imgsize, options = self.captured(
            CaptureRequest(time=0.25, imgsize='320x240'), 'out/shot.png')
        self.assertEqual(output, 'out/shot.png')
        self.assertEqual(imgsize, (320, 240))
        self.assertEqual(options['time'], 0.25)
        for key in ('view', 'up', 'fov'):
            self.assertNotIn(key, options)

    def test_a_requested_camera_is_resolved_and_handed_over(self):
        _, _, options = self.captured(CaptureRequest(camera='10,20,30,0,0,0'))
        self.assertEqual(options['view'], {'camera': [10, 20, 30],
                                           'target': [0, 0, 0]})
        self.assertEqual(options['up'], [0, 0, 1])
        self.assertEqual(options['fov'], 22.5)

    def test_a_negative_leading_vector_is_honoured(self):
        """A camera whose resolved up direction begins with a negative
        component reaches the page as the numbers it is."""
        for camera in ('0,0,0,65,0,35,1400', '-100,20,30,0,0,0'):
            with self.subTest(camera=camera):
                resolved = parse_camera(camera)
                _, _, options = self.captured(CaptureRequest(camera=camera))
                self.assertEqual(options['view'],
                                 {'camera': list(resolved.eye),
                                  'target': list(resolved.target)})
                self.assertEqual(options['up'], list(resolved.up))
        self.assertLess(parse_camera('0,0,0,65,0,35,1400').up[0], 0)

    def test_the_viewers_failure_is_its_message(self):
        from machinome.viewer.web.capture import CaptureError, PLAYWRIGHT_REMEDY
        with patch('machinome.viewer.web.capture.Capture') as capture:
            capture.return_value.render.side_effect = CaptureError(
                PLAYWRIGHT_REMEDY)
            with self.assertRaises(ViewerError) as raised:
                web.capture('/tmp/staged', CaptureRequest(), 'shot.png')
        self.assertEqual(str(raised.exception), PLAYWRIGHT_REMEDY)
        self.assertIn("machinome-viewer[snapshot]", PLAYWRIGHT_REMEDY)
        self.assertIn('playwright install chromium', PLAYWRIGHT_REMEDY)

    def test_a_missing_bundle_is_refused_before_staging(self):
        with patch('machinome.viewer.web.bundle.has_bundle',
                   return_value=False), \
             patch('machinome.viewer.web.bundle.missing_bundle_remedy',
                   return_value='Viewer bundle not found'):
            with self.assertRaises(ViewerError) as raised:
                stage_module.stage(Mock(), "/unused")
        self.assertEqual(str(raised.exception), 'Viewer bundle not found')

    def test_browser_failure_never_falls_back_to_openscad(self):
        snapshot = Snapshot()
        node = Mock()
        node.__class__.__name__ = "Part"

        def prepared():
            snapshot.presented = '/tmp/staged'
            return node

        with (
            patch.object(snapshot, "_load_and_prepare_node",
                         side_effect=prepared),
            patch("machinome.viewer.web.capture",
                  side_effect=ViewerError("browser missing")),
            patch("machinome.viewer.web.withdraw"),
            patch("machinome.viewer.openscad.capture") as openscad,
            patch("sys.stderr"),
        ):
            with self.assertRaises(SystemExit):
                snapshot.handle(snapshot_args())
        openscad.assert_not_called()


@needs_viewer
@unittest.skipUnless(
    os.environ.get('MACHINOME_WEB_SNAPSHOT_E2E'),
    'set MACHINOME_WEB_SNAPSHOT_E2E=1 to photograph through the installed viewer',
)
class BrowserSnapshotEndToEndTest(TestCase):
    """The whole path, through the real viewer: opt-in, because it needs
    the viewer's snapshot extra and a downloaded Chromium."""

    def test_a_transparent_photograph_is_written(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temporary:
            output = os.path.join(temporary, "web.png")
            Snapshot().handle(snapshot_args(
                path="tests/web_snapshot_project.py", imgsize="320x240",
                output=output))
            alpha = Image.open(output).convert("RGBA").getchannel("A")
            self.assertEqual(alpha.getpixel((0, 0)), 0)
            self.assertIn(255, alpha.getdata())


class UnreadableDocumentRefusalTest(TestCase):
    """(7.3) A capture is a one-shot: a document the installed viewer
    cannot read is refused BEFORE the browser starts, rather than
    surfacing as an opaque non-zero exit from a headless page."""

    def setUp(self):
        from tests.base import BUILD_DIR
        from machinome.simulation.enumeration import bind_declared_defaults
        from tests.running_project.machine import Train, TrainBody

        if os.path.exists(BUILD_DIR):
            shutil.rmtree(BUILD_DIR)
        os.makedirs(BUILD_DIR)
        self.addCleanup(shutil.rmtree, BUILD_DIR, ignore_errors=True)
        self.build_dir = BUILD_DIR
        self.running = Train()
        bind_declared_defaults(self.running)
        self.running.assemble()
        self.running.build_stls()
        self.untimed = TrainBody()
        bind_declared_defaults(self.untimed)
        self.untimed.assemble()
        self.untimed.build_stls()

    def siblings(self):
        parent = os.path.dirname(self.build_dir)
        return {name for name in os.listdir(parent)
                if 'web-snapshot' in name}

    def reading(self, versions):
        """The web viewer reading `versions`, its bundle present."""
        return (patch('machinome.viewer.web.bundle.has_bundle',
                      return_value=True),
                patch.object(web, 'document_versions', return_value=versions),
                patch.object(web, 'identity',
                             return_value=('machinome-viewer', '0.1.0')))

    def test_a_running_model_is_refused_naming_the_three_facts(self):
        before = self.siblings()
        bundle, versions, identity = self.reading([1, 2, 3, 4])
        with bundle, versions, identity, \
             patch('machinome.viewer.web.capture.Capture') as started:
            with self.assertRaises(ViewerError) as raised:
                web.present(self.running, self.build_dir)
        message = str(raised.exception)
        self.assertIn('document version 11', message)
        self.assertIn('the installed web viewer renders 1, 2, 3, 4', message)
        self.assertIn('0.1.0', message)
        self.assertIn('--viewer open' 's' 'cad', message)
        started.assert_not_called()
        self.assertEqual(self.siblings(), before)

    def test_a_viewer_that_can_read_it_stages_as_before(self):
        bundle, versions, identity = self.reading(list(range(1, 12)))
        with bundle, versions, identity:
            staging = stage_module.stage(self.running, self.build_dir)
        self.addCleanup(web.withdraw, staging)
        with open(os.path.join(staging, 'viewer.json')) as handle:
            document = json.load(handle)
        self.assertEqual(document['version'], 11)

    def test_a_baked_capture_publishes_no_controls(self):
        """A capture BAKES one instant: its tree holds numbers rather
        than expressions, it publishes an EMPTY instructions table for
        that reason, and a button naming an instruction that document
        does not list would be inconsistent. So the capture publishes no
        `controls` key, and is otherwise the document it always was
        (OpenSpec change `declare-controls-on-parts`, design section 9).
        """
        from machinome.simulation.enumeration import bind_declared_defaults
        from tests.running_project.machine import Columns

        controlled = Columns()
        bind_declared_defaults(controlled)
        controlled.assemble()
        controlled.build_stls()
        bundle, versions, identity = self.reading(list(range(1, 12)))
        with bundle, versions, identity:
            staging = stage_module.stage(controlled, self.build_dir)
        self.addCleanup(web.withdraw, staging)
        with open(os.path.join(staging, 'viewer.json')) as handle:
            document = json.load(handle)

        self.assertNotIn('controls', document)
        self.assertEqual(document['instructions'], {})
        self.assertEqual(document['version'], 11)
        self.assertIn('program', document)

    def test_an_untimed_model_is_unaffected(self):
        bundle, versions, identity = self.reading([1, 2, 3, 4])
        with bundle, versions, identity:
            staging = stage_module.stage(self.untimed, self.build_dir)
        self.addCleanup(web.withdraw, staging)
        with open(os.path.join(staging, 'viewer.json')) as handle:
            document = json.load(handle)
        self.assertLess(document['version'], 5)
