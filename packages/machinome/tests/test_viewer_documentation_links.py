"""Readers can reach the independent viewer manual from the framework."""

from pathlib import Path
import pytest

DOCS = Path(__file__).resolve().parents[1] / 'docs'
MANUAL = 'https://machinome-viewer.readthedocs.io/en/latest/'


@pytest.mark.parametrize(('page', 'target'), [
    ('reference/manuals.rst', ''),
    ('concepts/publishing.rst', 'embedding.html'),
    ('tutorial/10-share.rst', 'embedding.html'),
])
def test_viewer_manual_is_linked(page, target):
    assert MANUAL + target in (DOCS / page).read_text()
