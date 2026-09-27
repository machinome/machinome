# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Physical endpoints for Bounds, installed limits and explicit controls.

Relations and author bindings still address the mate's assembly port. Only
these mechanical contracts follow it to the existing posing child joint.
"""

def is_mate(value):
    return getattr(type(value), 'mate_kind', None) == 'mate'


def scoped_ref(ref, owner):
    """Rewalk a written descendant path on the effective declaring class."""
    from .couplings import PathRef
    from machinome.node.declarative import ChildDeclaration, declared_children

    if not isinstance(ref, PathRef):
        return ref
    root = declared_children(owner).get(ref.root._name)
    if not isinstance(root, ChildDeclaration):
        raise TypeError(f'{owner.__name__}: mechanical path {ref.written} '
                        'does not start at one declared child')
    found = PathRef(root, (), root)
    for segment in ref.segments:
        found = getattr(found, segment)
    return found


def declaration(ref):
    from .couplings import PathRef

    return ref.terminal if isinstance(ref, PathRef) else ref.declaration()


def posing_joint(ref):
    declared = declaration(ref)
    if not is_mate(declared):
        return declared
    if declared.freedom is None:
        from .mates import _owns_no_coordinate
        raise TypeError(_owns_no_coordinate(ref.described()))
    # During the executing class body installation has not happened yet.
    return declared.joint if declared.joint is not None else declared.freedom


def endpoint_key(ref, owner):
    """Canonical physical identity in one declaring class's subtree."""
    from .couplings import PathRef
    from .joints import Joint
    from machinome.node.declarative import ChildDeclaration

    ref = scoped_ref(ref, owner)
    declared = declaration(ref)
    if isinstance(ref, PathRef):
        path = (ref.root._name,) + ref.segments
        if is_mate(declared):
            posing_joint(ref)
            path = path[:-1] + (declared.moving.root._name, declared.name)
        elif isinstance(declared, ChildDeclaration):
            # A node used as a read stands for its one scalar joint,
            # exactly as it does in a relation. It is the same physical
            # endpoint as a path explicitly naming that joint.
            path += (ref.declaration().name,)
        return ('coordinate', path)
    if is_mate(declared):
        posing_joint(ref)
        return ('coordinate', (declared.moving.root._name, declared.name))
    if isinstance(declared, Joint) or getattr(declared, 'domain', None) is not None:
        return ('coordinate', (declared.name,)) if declared.name is not None else ref.key()
    return ref.key()


def check_read(ref, owner, bound):
    """Check written ownership, then an inherited effective path and kind."""
    from .couplings import OwnRef, PathRef
    from machinome.node.declarative import declared_children

    declared = declaration(ref)
    if isinstance(ref, OwnRef) and is_mate(declared):
        # Descriptor checks precede declare_mates in NodeMeta. The own
        # declaration is already in the MRO even though its table is not.
        if not any(vars(base).get(declared.name) is declared for base in owner.__mro__):
            ref.check_declared_on(owner, bound)
    else:
        if isinstance(ref, PathRef) and not any(
                declared_children(base).get(ref.root._name) is ref.root
                for base in owner.__mro__):
            # A shared spelling is not authority to redirect another
            # class's declaration into this tree. Only this owner or an
            # actual base may supply the written path being rechecked.
            ref.check_declared_on(owner, bound)
        effective = scoped_ref(ref, owner)
        effective.check_declared_on(owner, bound)
        if (effective.domain != ref.domain or effective.unit != ref.unit):
            raise TypeError(f'{owner.__name__}: {bound.described()} reads '
                            f'{ref.described()} with an incompatible domain or unit')
    return endpoint_key(ref, owner)


def resolve_endpoint(ref, owner):
    """Resolve lazily, after the complete realized tree has been linked."""
    from .couplings import ResolvedEnd
    from .joints import declared_joints

    ref = scoped_ref(ref, type(owner))
    end = ref.resolve(owner)
    if not is_mate(end.declared):
        return end
    mate = end.declared
    posing_joint(ref)
    child = getattr(end.node, mate.moving.root._name)
    joint = declared_joints(type(child))[mate.name]
    return ResolvedEnd(child, joint, ref)


def check_reads(bound, owner, target_key):
    seen = set()
    for ref in bound.reads:
        key = check_read(ref, owner, bound)
        if key == target_key:
            raise TypeError(f'{owner.__name__}: {bound.described()} reads its '
                            'OWN coordinate; drop it from reads=')
        if key in seen:
            raise TypeError(f'{owner.__name__}: {bound.described()} reads '
                            f'{ref.described()} twice')
        seen.add(key)
