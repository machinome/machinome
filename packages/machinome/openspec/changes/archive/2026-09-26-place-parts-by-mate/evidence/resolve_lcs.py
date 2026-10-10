"""Spike: re-derive Thor's transcribed placements from the design's own frames.

Assembly4 stores, per link: AttachedBy (the child's own LCS), AttachedTo
(parent object # parent LCS) and AttachmentOffset. The solved Placement
it also stores should equal

    parent_placement o parent_LCS o offset o inverse(child_LCS)

which is the mate rule of mates-and-sketches.md section 5.2 plus one offset.
"""
import sys, os, math, zipfile
import xml.etree.ElementTree as ET
sys.path.insert(0, '/mnt/data/machinome-projects/Robotic-Arms/Thor')
from simulation.tools import freecad_doc as fd
from simulation import layout

IDENT = fd.IDENTITY

class Doc(fd.Document):
    def __init__(self, path):
        super().__init__(path)
        root = ET.fromstring(self.zip.read('Document.xml'))
        self.attach = {}
        for node in root.find('ObjectData'):
            name = node.get('name')
            props = {p.get('name'): p for p in node.find('Properties')}
            def val(k):
                p = props.get(k)
                if p is None or not list(p): return None
                return list(p)[0]
            by, to, off = val('AttachedBy'), val('AttachedTo'), val('AttachmentOffset')
            if by is not None and to is not None:
                a = off.attrib if off is not None else None
                offm = fd.matrix_from_quaternion(
                    (float(a['Q0']), float(a['Q1']), float(a['Q2']), float(a['Q3'])),
                    (float(a['Px']), float(a['Py']), float(a['Pz']))) if a else IDENT
                self.attach[name] = (by.get('value'), to.get('value'), offm)

    def frames_under(self, name, parent=IDENT, out=None, follow_links=True):
        """Every object's composed matrix below `name`, keyed by object name."""
        if out is None: out = {}
        obj = self.objects.get(name)
        if obj is None: return out
        m = fd.compose(parent, self.matrix(obj)) if obj['placement'] else parent
        out.setdefault(name, m)
        for child in obj['group'] + obj['elements']:
            self.frames_under(child, m, out)
        if follow_links and obj['link'] and obj['link'][0] is None:
            self.frames_under(obj['link'][1], m, out)
        return out

docs = {}
def doc(name):
    if name not in docs:
        for f in os.listdir(fd.FREECAD_DIR):
            if f.lower() == (name + '.fcstd').lower():
                docs[name] = Doc(os.path.join(fd.FREECAD_DIR, f)); break
        else:
            raise KeyError('no document for %s' % name)
    return docs[name]

def roots(document):
    referenced = set()
    for o in document.objects.values():
        referenced.update(o['group']); referenced.update(o['elements'])
    return [n for n in document.objects if n not in referenced]

def lcs_in(document, holder, lcs):
    """A frame's matrix in the frame of `holder` (an object in `document`).

    `holder` is 'Model' for an external part document; when that document
    has no Model, every root object is walked instead."""
    if holder in document.objects:
        frames = document.frames_under(holder, IDENT)
    else:
        frames = {}
        for r in roots(document):
            document.frames_under(r, IDENT, frames)
    if lcs in frames:
        return frames[lcs]
    raise KeyError('%s has no %s under %s (roots %s)' % (document.path, lcs, holder, roots(document)[:6]))

def child_frame(document, link_obj, lcs):
    """The child's own LCS, in the child's own (Model) frame."""
    src, target = link_obj['link']
    if src:   # external document: LCS lives under its Model
        d = doc(src.split('.')[0])
        return lcs_in(d, 'Model', lcs)
    return lcs_in(document, target, lcs)   # bought part: an in-document App::Part

def resolve(document, link_obj):
    by, to, off = document.attach[link_obj['name']]
    by = by.lstrip('#')
    parent_name, parent_lcs = to.split('#')
    if parent_name == 'Parent Assembly':
        parent_m = IDENT
        pframe = lcs_in(document, 'Model', parent_lcs) if parent_lcs != 'LCS_Origin' else IDENT
    else:
        pobj = document.objects[parent_name]
        parent_m = document.matrix(pobj)
        pframe = child_frame(document, pobj, parent_lcs)
    cframe = child_frame(document, link_obj, by)
    return fd.compose(fd.compose(fd.compose(parent_m, pframe), off), fd.invert(cframe)), (by, to, pframe, cframe, off)

def close(a, b, tol=1e-3):
    Ra, ta = a; Rb, tb = b
    return all(abs(Ra[i][j]-Rb[i][j]) < tol for i in range(3) for j in range(3)) and all(abs(ta[i]-tb[i]) < tol for i in range(3))

def fmt(M):
    axis, ang = fd.axis_angle(M[0])
    return 't=(%s) rot %.2f about (%s)' % (', '.join('%.2f' % v for v in M[1]), ang, ', '.join('%.3f' % v for v in axis))

groups = ['Assembly'] + list(fd.SUB_ASSEMBLIES)
ok = bad = 0
for g in groups:
    d = doc(g)
    print('=====', g)
    for link in d.part_links():
        if link['name'] not in d.attach:
            print('  (no attachment)', link['label']); continue
        try:
            got, (by, to, pframe, cframe, off) = resolve(d, link)
        except KeyError as e:
            print('  ?', link['label'], e); bad += 1; continue
        want = d.matrix(link)
        flag = 'ok ' if close(got, want) else 'BAD'
        if flag == 'BAD': bad += 1
        else: ok += 1
        if g in ('Assembly', 'AssemblyArt2', 'AssemblyArt3') or flag == 'BAD':
            print('  %s %-45s by %-24s to %-45s' % (flag, link['label'], by, to))
            if g == 'Assembly' or flag == 'BAD' or link['label'] in ('Art2BodyA_Art2BodyA', 'Art3Pulley_Art3Pulley', 'Art3Body_Art3Body', 'Bearing_625ZZ001', '5x128mm001'):
                print('       parent frame  %s' % fmt(pframe))
                print('       child frame   %s' % fmt(cframe))
                print('       offset        %s' % fmt(off))
                print('       resolved      %s' % fmt(got))
                print('       design stored %s' % fmt(want))
print('ok', ok, 'bad', bad)
