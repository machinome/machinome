"""Readers reach the browser viewer's pages inside the manual.

The viewer's manual is part of this one (change `join-viewer`): the
framework's pages that sent a reader to a separate viewer manual link its
how-to guides and its reference section here, and no page links the
separate manual.
"""

import re
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


# The viewers are documented as chosen by name (change `viewer-seam`,
# capability `user-documentation`).

#: A paragraph of a page: text between blank lines.
PARAGRAPH = '\n\n'


def current_text(page):
    """What of `page` a reader takes as current: the changelog's
    `Unreleased` section alone, the upgrading page's 0.9 section alone, and
    every other page whole."""
    text = (DOCS / page).read_text()
    if page == 'project/changelog.rst':
        start = text.index('Unreleased')
        following = text.find('\nMachinome 0.', start)
        return text[start:following if following >= 0 else None]
    if page == 'project/upgrading.rst':
        start = text.find('Upgrading from Machinome 0.8 to 0.9')
        end = text.find('Upgrading from Machinome 0.8.0 to 0.8.1')
        return text[start:end] if start >= 0 else ''
    return text


def former_flag_offences(text):
    """The paragraphs of `text` that spell the former flag other than to say
    it is refused."""
    return [paragraph.strip()[:60] for paragraph in text.split(PARAGRAPH)
            if '--renderer' in paragraph and 'refuse' not in paragraph]


def test_no_current_page_spells_the_former_flag():
    pages = [page.relative_to(DOCS).as_posix()
             for page in sorted(DOCS.rglob('*.rst'))
             if '_build' not in page.relative_to(DOCS).parts]
    offending = {page: former_flag_offences(current_text(page))
                 for page in pages}
    assert {page: found for page, found in offending.items() if found} == {}


def test_the_rule_reads_a_refusal_as_no_offence():
    assert former_flag_offences(
        'Take it with ``--renderer web``.\n\n``--renderer`` is refused, '
        'naming ``--viewer``.') == ['Take it with ``--renderer web``.']


def test_the_upgrading_page_begins_the_0_9_section():
    text = (DOCS / 'project' / 'upgrading.rst').read_text()
    assert text.index('Upgrading from Machinome 0.8 to 0.9') \
        < text.index('Upgrading from Machinome 0.8.0 to 0.8.1')
    section = ' '.join(current_text('project/upgrading.rst').split())
    for spelled in ('The viewer flag', '``--viewer``', '``--renderer``',
                    '[tool.machinome]', 'machinome[viewer-openscad]',
                    'machinome viewer'):
        assert spelled in section, spelled


def test_the_tutorial_takes_its_web_still_with_the_viewer_flag():
    text = (DOCS / 'tutorial' / '10-share.rst').read_text()
    assert ('$ machinome snapshot --viewer web --drive crank=3580 -o '
            'carry.png') in text


def test_the_how_to_chooses_the_viewer_of_a_still():
    text = (DOCS / 'howto' / 'share-an-export.rst').read_text()
    assert '\nChoose the viewer of a still\n' in text
    section = ' '.join(text[text.index('Choose the viewer of a still'):]
                       .split())
    for spelled in ('--viewer web', '--viewer openscad', 'viewer = "web"',
                    '[tool.machinome]', '--projection', '--colorscheme'):
        assert spelled in section, spelled


@pytest.mark.parametrize('command', ['snapshot', 'develop', 'export'])
def test_the_command_reference_names_the_viewer_flag(command):
    text = (DOCS / 'reference' / 'cli.rst').read_text()
    start = text.index(f'machinome {command}\n')
    following = re.search(r'\nmachinome \w', text[start + 1:])
    section = text[start:start + 1 + following.start()
                   if following else None]
    assert '--viewer' in section, command


# The installation page lists the OpenSCAD viewer's extra and the
# distribution it installs through its rendered list since change
# `manual-extras`, which tests/test_manual_extras.py holds for every extra
# of the manifest.
