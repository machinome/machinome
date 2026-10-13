# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The manual's own Sphinx extension: every page declares the extras it
needs (change `manual-extras`, ADR-195).

``.. needs:: movie``, or ``.. needs:: none``, is the first thing under a
page's title. It records the page's extras and renders, for a page that
needs some, one line at the top of the page: the ``pip install`` line those
extras make, and what they need outside pip. ``.. extras::`` renders the
installation page's list of every extra the framework's manifest declares
for a reader: the distributions it installs, read from the manifest; what it
is for and what it needs outside pip, read from the table beside this
module, ``manual_extras.toml``; and the pages that declare it.

The build fails, under warnings as errors, on a page that declares nothing,
a declaration naming an extra the table lacks, an extra twice or ``none``
with another, a declaration that is not the first thing under the title or
is the page's second, and a table whose extras are not the manifest's.

Settings: ``manual_extras_manifest``, the framework's manifest relative to
the configuration directory, and ``manual_extras_exempt``, ``fnmatch``
patterns of the documents that declare nothing.

The module imports Sphinx, docutils, ``packaging`` (a requirement of Sphinx)
and the standard library, so the manual builds from its requirements alone.
"""

import fnmatch
import re
import tomllib
from pathlib import Path

from docutils import nodes
from packaging.requirements import Requirement
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

logger = logging.getLogger(__name__)

#: The table of extras, beside this module.
TABLE = Path(__file__).with_suffix('.toml')

#: The extras of the manifest a contributor installs, which the manual does
#: not list.
CONTRIBUTOR = ('dev', 'docs')

#: The class of the line a page shows under its title, styled by
#: ``_static/manual-extras.css``.
NEEDS_CLASS = 'machinome-needs'


def read_table():
    """The table of extras, {extra: {'for': str, 'outside': [str]}}, in
    the order the installation page lists them."""
    return tomllib.loads(TABLE.read_text())


def resolve_manifest(app, config):
    """The manifest's path, made absolute from the configuration
    directory once the configuration is read."""
    config.manual_extras_manifest = str(
        Path(app.confdir, config.manual_extras_manifest).resolve())


def read_manifest(config):
    """The manifest's extras, {extra: [requirement]}."""
    path = Path(config.manual_extras_manifest)
    project = tomllib.loads(path.read_text())['project']
    return project['optional-dependencies']


def members(requirements):
    """The extras of the framework a requirement list names, as
    ``machinome[a,b]`` does."""
    found = []
    for line in requirements:
        requirement = Requirement(line)
        if requirement.name == 'machinome':
            found += sorted(requirement.extras)
    return found


def outside(extras, table, manifest):
    """What `extras` need outside pip, an extra that names other extras of
    the framework standing for its members, each phrase once."""
    phrases = []
    for name in extras:
        named = [extra for extra in members(manifest.get(name, ()))
                 if extra in table]
        for extra in [name, *in_table_order(named, table)]:
            phrases += table.get(extra, {}).get('outside', [])
    return list(dict.fromkeys(phrases))


def joined(items):
    """'a', 'a and b', 'a, b and c'."""
    items = list(items)
    if len(items) < 2:
        return ''.join(items)
    return ', '.join(items[:-1]) + ' and ' + items[-1]


def in_table_order(names, table):
    order = list(table)
    return sorted(names, key=order.index)


class extras_pages(nodes.General, nodes.Element):
    """Where an entry of the list names the pages that declare its extra,
    filled once every page is read."""


class NeedsDirective(SphinxDirective):
    """``.. needs:: <extras>`` or ``.. needs:: none``."""

    required_arguments = 1
    final_argument_whitespace = True

    def run(self):
        table = read_table()
        names = [name.strip() for name in self.arguments[0].split(',')]
        if names != ['none']:
            for name in names:
                if name not in table:
                    raise self.error(f"needs: {name} is not an extra of the "
                                     "manual's table")
            for name in names:
                if names.count(name) > 1:
                    raise self.error(f'needs: {name} is named twice')
        declared = self.env.__dict__.setdefault('manual_extras', {})
        section = self.state.parent
        before = [child for child in section.children
                  if not isinstance(child, nodes.system_message)]
        first = (isinstance(section, nodes.section)
                 and isinstance(section.parent, nodes.document)
                 and len(before) == 1
                 and isinstance(before[0], nodes.title))
        if not first or self.env.docname in declared:
            raise self.error("needs: the declaration is the first thing "
                             "under the page's title, and the page's only one")
        extras = () if names == ['none'] else tuple(
            in_table_order(names, table))
        declared[self.env.docname] = extras
        if not extras:
            return []
        manifest = read_manifest(self.config)
        text = (f':ref:`Needs <extras>` ``pip install '
                f'"machinome[{",".join(extras)}]"``')
        steps = outside(extras, table, manifest)
        if steps:
            text += ', and outside pip: ' + '; '.join(steps)
        inline, messages = self.state.inline_text(text + '.', self.lineno)
        box = nodes.container(classes=[NEEDS_CLASS])
        box += nodes.paragraph('', '', *inline)
        return [box, *messages]


class ExtrasDirective(SphinxDirective):
    """``.. extras::``: the list of every extra a reader installs."""

    def installs(self, requirements, table):
        """What an extra's requirements install, as inline reST."""
        found = []
        for line in requirements:
            requirement = Requirement(line)
            extras = sorted(requirement.extras)
            if requirement.name == 'machinome':
                found.append('the extras ' + joined(
                    f'``{name}``' for name in in_table_order(
                        [name for name in extras if name in table], table)))
            elif extras:
                found.append(f'``{requirement.name}`` with its '
                             + joined(f'``{name}``' for name in extras)
                             + (' extras' if len(extras) > 1 else ' extra'))
            else:
                found.append(f'``{requirement.name}``')
        return joined(found) or 'nothing the manifest declares'

    def run(self):
        table = read_table()
        manifest = read_manifest(self.config)
        listed = nodes.definition_list(classes=['machinome-extras'])
        for name, row in table.items():
            text = (f'Installs {self.installs(manifest.get(name, ()), table)}'
                    f', for {row["for"]}.')
            steps = outside([name], table, manifest)
            if steps:
                text += f' Outside pip: {"; ".join(steps)}.'
            inline, messages = self.state.inline_text(text, self.lineno)
            definition = nodes.definition()
            definition += nodes.paragraph('', '', *inline)
            definition += messages
            definition += extras_pages(extra=name)
            item = nodes.definition_list_item()
            item += nodes.term('', '', nodes.literal(
                '', f'machinome[{name}]'))
            item += definition
            listed += item
        return [listed]


def purge(app, env, docname):
    env.__dict__.get('manual_extras', {}).pop(docname, None)


def merge(app, env, docnames, other):
    declared = env.__dict__.setdefault('manual_extras', {})
    for docname, extras in other.__dict__.get('manual_extras', {}).items():
        if docname in docnames:
            declared[docname] = extras


def check(app, env):
    """Every page declares, and the table is the manifest's."""
    declared = env.__dict__.get('manual_extras', {})
    exempt = app.config.manual_extras_exempt
    for docname in sorted(env.found_docs):
        if docname in declared or any(fnmatch.fnmatch(docname, pattern)
                                      for pattern in exempt):
            continue
        logger.warning('the page declares no extra: begin it, under its '
                       'title, with `.. needs::` and the extras a reader '
                       'installs to follow it, or `none`', location=docname)
    table = sorted(read_table())
    manifest = sorted(set(read_manifest(app.config))
                      - set(CONTRIBUTOR))
    if table != manifest:
        logger.warning(f"the manual's table of extras {table} is not the "
                       f"manifest's {manifest}: give docs/_ext/{TABLE.name} "
                       "a row for each extra of the manifest but "
                       f"{' and '.join(CONTRIBUTOR)}, and only those")


#: A reference section's page: reference/<section>/<page>.
SECTION = re.compile(r'^reference/([^/]+)/[^/]+$')


def standing_for(docname, needing):
    """The document that stands for `docname` in an entry's pages: the
    tutorial by its first declaring chapter, a reference section's page by
    the section's index when the index declares the extra too."""
    if docname.startswith('tutorial/'):
        return min(name for name in needing if name.startswith('tutorial/'))
    found = SECTION.match(docname)
    if found:
        index = f'reference/{found.group(1)}/index'
        if index in needing:
            return index
    return docname


def resolve(app, doctree, fromdocname):
    """Fills each entry's pages, once every page's declaration is known."""
    env = app.env
    declared = env.__dict__.get('manual_extras', {})
    for node in list(doctree.findall(extras_pages)):
        needing = sorted(docname for docname, extras in declared.items()
                         if node['extra'] in extras)
        pages = list(dict.fromkeys(standing_for(docname, needing)
                                   for docname in needing))
        if not pages:
            node.replace_self([])
            continue
        links = []
        for docname in pages:
            title = ('the tutorial' if docname.startswith('tutorial/')
                     else env.titles[docname].astext())
            link = nodes.reference('', title, internal=True,
                                   refuri=app.builder.get_relative_uri(
                                       fromdocname, docname))
            links.append(link)
        paragraph = nodes.paragraph('', 'Needed by ')
        for number, link in enumerate(links):
            if number:
                paragraph += nodes.Text(
                    ' and ' if number == len(links) - 1 else ', ')
            paragraph += link
        paragraph += nodes.Text('.')
        node.replace_self(paragraph)


def setup(app):
    app.add_config_value('manual_extras_manifest', '../pyproject.toml', 'env')
    app.add_config_value('manual_extras_exempt', [], 'env')
    app.connect('config-inited', resolve_manifest)
    app.add_node(extras_pages)
    app.add_directive('needs', NeedsDirective)
    app.add_directive('extras', ExtrasDirective)
    app.connect('env-purge-doc', purge)
    app.connect('env-merge-info', merge)
    app.connect('env-check-consistency', check)
    app.connect('doctree-resolved', resolve)
    app.add_css_file('manual-extras.css')
    return {'version': '1', 'env_version': 1,
            'parallel_read_safe': True, 'parallel_write_safe': True}
