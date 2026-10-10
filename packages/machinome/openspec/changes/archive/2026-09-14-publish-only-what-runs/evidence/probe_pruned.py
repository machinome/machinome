"""What the candidate fix would publish, measured WITHOUT changing the
framework.

`pruned()` reproduces the proposed rule on an already-compiled program:
`Program.nodes` is reduced to the bank plus the ends of the edges
`_reaching_the_bank` kept, and `sources` is recomputed off the reduced
table. Nothing else is touched -- in particular `identity`, which is a
digest of `described()`, and `described()` reads the inputs, the
coordinates, the spans and the edges, never `nodes`.

Three things are measured:

 1. the two refusals go away (probe_repeat_port.py's `Bank`,
    probe_omitted.py's `Machine(fitted=False)`), and what they publish
    instead;
 2. a KEPT edge with an unqualified end still refuses
    (probe_omitted.py's `Reader(fitted=False)`);
 3. the blast radius: every running fixture in `tests/running_project`
    whose published document carries a name the rule removes, and
    whether any expression in that document reads it.

Run from the worktree root with PYTHONPATH="$PWD".
"""

import inspect
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solid_node.node import AssemblyNode                       # noqa: E402
from solid_node.simulation.enumeration import (                # noqa: E402
    bind_declared_defaults)
from solid_node.simulation.program import (                    # noqa: E402
    _reaching_inputs, program_of)

from probe_omitted import Machine, Reader                      # noqa: E402
from probe_repeat_port import Bank                             # noqa: E402


def pruned(program):
    """The proposed rule, applied to a compiled program. Returns the
    names it removed."""
    live = set(program.bank_keys)
    for edge in program.edges:
        live.update(edge.needs)
        live.update(edge.gives)
    dropped = [key for key in program.nodes if key not in live]
    names = sorted(program.nodes[key].name for key in dropped)
    for key in dropped:
        del program.nodes[key]
    program.sources = _reaching_inputs(program.nodes, program.edges)
    return names


def publish(label, factory):
    try:
        node = factory()
        bind_declared_defaults(node)
        program, initial = program_of(node)
    except Exception as error:
        print(f'{label}: compile -> {type(error).__name__}: {error}')
        return
    before = program.identity
    names = sorted(entry.name for entry in program.nodes.values())
    removed = pruned(program)
    print(f'{label}: nodes before  {names}')
    print(f'{label}: removed       {removed}')
    print(f'{label}: identity unchanged: {before == program.identity}')
    try:
        published = program.published(initial)
    except Exception as error:
        print(f'{label}: published -> {type(error).__name__}: {error}')
        return
    print(f'{label}: coordinates   {sorted(published["coordinates"])}')
    print(f'{label}: intermediates {published["intermediates"]}')
    print(f'{label}: sources       {json.dumps(published["sources"])}')


def blast_radius():
    """Every running fixture whose document loses a name, and whether
    the document reads it."""
    sys.path.insert(0, os.getcwd())
    from tests.test_running_document import document, names_in
    import tests.running_project.machine as machine

    for name, value in sorted(vars(machine).items()):
        if not (inspect.isclass(value)
                and issubclass(value, AssemblyNode)
                and value.__module__ == machine.__name__):
            continue
        try:
            node = value()
            bind_declared_defaults(node)
            program, _initial = program_of(node)
        except Exception:
            continue
        removed = set(pruned(program))
        if not removed:
            continue
        node = value()
        bind_declared_defaults(node)
        published = document(node)
        read = names_in(published)
        bindings = ' '.join(entry['expression']
                            for entry in published.get('bindings', ()))
        print(f'{name}: loses {sorted(removed)}; '
              f'read by an expression: '
              f'{sorted(item for item in removed if item in read)}; '
              f'named in the bindings table: '
              f'{sorted(item for item in removed if item in bindings)}')


def corpus_radius():
    """The committed conformance corpus carries each machine's document,
    so a name the rule removes has to come out of it too."""
    with open(os.path.join('tests', 'running-corpus.json')) as handle:
        fixture = json.load(handle)
    for entry in fixture['machines']:
        program = entry['document']['program']
        if program['intermediates']:
            print(f"corpus {entry['name']} dt={entry['dt']}: "
                  f"intermediates {program['intermediates']}, "
                  f"sources of each "
                  f"{ {name: program['sources'][name]
                       for name in program['intermediates']} }")


if __name__ == '__main__':
    publish('repeat port  ', Bank)
    publish('fitted=False ', lambda: Machine(fitted=False))
    publish('read=False   ', lambda: Reader(fitted=False))
    print()
    blast_radius()
    print()
    corpus_radius()
