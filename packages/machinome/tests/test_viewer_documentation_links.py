"""Readers reach the browser viewer's pages inside the manual.

The viewer's manual is part of this one (change `join-viewer`): the
framework's pages that sent a reader to a separate viewer manual link its
how-to guides and its reference section here, and no page links the
separate manual.
"""

from pathlib import Path
import pytest

DOCS = Path(__file__).resolve().parents[1] / 'docs'
README = Path(__file__).resolve().parents[1] / 'README.rst'
SEPARATE = 'machinome-viewer.readthedocs.io'


@pytest.mark.parametrize(('page', 'target'), [
    ('reference/manuals.rst', '/reference/viewer/index'),
    ('concepts/publishing.rst', '/howto/browser-viewer'),
    ('concepts/publishing.rst', '/reference/viewer/index'),
    ('concepts/publishing.rst', '/howto/embed-the-viewer'),
    ('tutorial/10-share.rst', '/howto/embed-the-viewer'),
    ('start/install.rst', '/howto/browser-viewer'),
])
def test_the_viewer_s_pages_are_linked_inside_the_manual(page, target):
    text = ' '.join((DOCS / page).read_text().split())
    assert (f':doc:`{target}`' in text
            or f'<{target}>`' in text), f'{page} does not link {target}'


def test_no_page_links_the_separate_viewer_manual():
    pages = [page for page in sorted(DOCS.rglob('*.rst'))
             if '_build' not in page.relative_to(DOCS).parts]
    linking = [page.relative_to(DOCS).as_posix() for page in pages
               if SEPARATE in page.read_text()]
    if SEPARATE in README.read_text():
        linking.append('README.rst')
    assert linking == []
