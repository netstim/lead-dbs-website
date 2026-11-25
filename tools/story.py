"""Packs the data of the home page's scroll story into assets/data/story.json.

The story (assets/js/story.js) is drawn from data in MNI space (ICBM 2009b nonlinear asymmetric), all of
the left hemisphere unless said:

- the leads: both electrodes of one Lead Tutor patient (its reconstruction file), the left one first;
- the nuclei: STN, GPi and RN of the DISTAL atlas (Ewert 2017), caudate and putamen of the OCD Response
  Tract Atlas, as stacked outlines;
- the fibres: the tract associated with good response in the OCD Response Tract Atlas (Li 2020), each
  from its back end forwards;
- the ALIC target of the DBS targets atlas (Horn 2017), both sides: where the story sets hypothetical leads;
- the OCD sweet and sour spot of the Human Dysfunctome Atlas (Hollunder 2024), as stacked outlines;
- the brain: a drawing of the template's cortex in the view the story ends on (assets/images/story-brain.png).

Run it on a computer with a Lead-DBS `templates` folder (numpy, scipy, nibabel, contourpy, h5py, pillow):

    python3 tools/story.py /path/to/templates/space/MNI152NLin2009bAsym \
        /path/to/derivatives/leaddbs/sub-XXXXX/reconstruction/sub-XXXXX_desc-reconstruction.mat

Coordinates are written as integers in units of 0.05 mm. Nothing is fetched.
"""
import argparse
import json
from pathlib import Path

import contourpy
import h5py
import nibabel as nib
import numpy as np
import pyvista as pv
import scipy.io as sio
from scipy import ndimage
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
UNIT = 0.05
SEED = 7
FIBRES = 170
POINTS = 96


def q(a):
    return np.round(np.asarray(a, float) / UNIT).astype(int).ravel().tolist()


def simplify(pts, tol):
    """Douglas-Peucker on an open polyline (n, 3)."""
    pts = np.asarray(pts, float)
    if len(pts) < 3:
        return pts
    keep = np.zeros(len(pts), bool)
    keep[[0, -1]] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        ab = pts[b] - pts[a]
        n = np.linalg.norm(ab)
        rel = pts[a + 1:b] - pts[a]
        d = np.linalg.norm(rel, axis=1) if n < 1e-9 else np.linalg.norm(np.cross(rel, ab / n), axis=1)
        i = int(d.argmax())
        if d[i] > tol:
            keep[a + 1 + i] = True
            stack += [(a, a + 1 + i), (a + 1 + i, b)]
    return pts[keep]


def nucleus(path, step=0.66, tol=0.06, left=False, sign=1, smooth=0, level=0.5, rel=0):
    """Outlines of a nucleus on axial planes `step` mm apart, as closed loops in mm."""
    img = nib.load(str(path))
    vol = img.get_fdata() * sign  # sign -1: the outline of the negative part of a map
    if smooth:                    # a map of values, not a mask: ease it, so its outline is one form
        vol = ndimage.gaussian_filter(np.nan_to_num(vol), smooth)
    if rel:                       # the level as a share of the map's peak
        level = rel * vol.max()
    aff = img.affine
    if left:                      # an image of both sides: keep the left one
        x = (aff @ np.c_[np.arange(vol.shape[0]), np.zeros((vol.shape[0], 2)), np.ones(vol.shape[0])].T)[0]
        vol = vol * (x < 0)[:, None, None]
    dz = abs(aff[2, 2])
    loops = []
    ks = np.arange(0, vol.shape[2], max(1, round(step / dz)))
    for k in ks:
        sl = vol[:, :, int(k)]
        if sl.max() < level:
            continue
        gen = contourpy.contour_generator(z=sl.T, name='serial')
        for line in gen.lines(level):
            if len(line) < 16:
                continue
            ijk = np.c_[line[:, 0], line[:, 1], np.full(len(line), k), np.ones(len(line))]
            xyz = (aff @ ijk.T).T[:, :3]
            xyz = simplify(xyz, tol)
            if len(xyz) >= 6:
                loops.append(q(xyz))
    return loops


def surface(path, faces=600, left=False, sign=1, smooth=0, level=0.5, rel=0):
    """The surface of a nucleus (or of one sign of a map) as a small mesh: points in mm, triangles wound
    so that their normals point outwards."""
    img = nib.load(str(path))
    vol = np.nan_to_num(img.get_fdata()) * sign
    aff = img.affine
    if left:
        x = (aff @ np.c_[np.arange(vol.shape[0]), np.zeros((vol.shape[0], 2)), np.ones(vol.shape[0])].T)[0]
        vol = vol * (x < 0)[:, None, None]
    vol = ndimage.gaussian_filter(vol.astype(float), max(smooth, 0.8))
    if rel:
        level = rel * vol.max()
    # only the box the form lies in, at a spacing coarse enough for a few thousand triangles
    idx = np.argwhere(vol > level)
    lo, hi = np.maximum(idx.min(0) - 2, 0), np.minimum(idx.max(0) + 3, vol.shape)
    vol = vol[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]
    step = max(1, int(round((np.prod(vol.shape) / 60000) ** (1 / 3))))
    if step > 1:
        vol = ndimage.gaussian_filter(vol, step * 0.5)[::step, ::step, ::step]
    vol = np.pad(vol, 1)
    grid = pv.ImageData(dimensions=vol.shape)
    grid['v'] = vol.ravel(order='F')
    m = grid.contour([level], scalars='v').connectivity('largest').triangulate().clean()
    m = m.smooth_taubin(n_iter=60, pass_band=0.02)
    if m.n_cells > faces:
        m = m.decimate(1 - faces / m.n_cells).clean()
    m = m.compute_normals(auto_orient_normals=True, consistent_normals=True, split_vertices=False)
    ijk = (np.asarray(m.points) - 1) * step + lo
    xyz = (aff @ np.c_[ijk, np.ones(len(ijk))].T).T[:, :3]
    f = np.asarray(m.faces).reshape(-1, 4)[:, 1:]
    # outwards: the volume enclosed must come out positive
    a, b, c = xyz[f[:, 0]], xyz[f[:, 1]], xyz[f[:, 2]]
    if np.einsum('ij,ij->i', a, np.cross(b, c)).sum() < 0:
        f = f[:, ::-1]
    return {'v': q(xyz), 'f': f.ravel().tolist()}


def fibres(path, tip, rng):
    """The fibres of the positive tract on the left, each from its back end forwards; the first one is
    the fibre the story follows: one that passes the lead closely and runs far forwards."""
    f = h5py.File(str(path), 'r')
    cell = f[f['fibcell'][1, 0]]          # the second group: associated with good response
    lines = []
    for i in range(cell.shape[1]):
        p = np.array(f[cell[0, i]], float)
        p = p.T if p.shape[0] == 3 else p
        if p[:, 0].mean() > 0:
            continue
        if p[0, 1] > p[-1, 1]:
            p = p[::-1]          # from the back forwards
        if np.linalg.norm(np.diff(p, axis=0), axis=1).sum() > 30:
            lines.append(p)
    near = np.array([np.linalg.norm(p - tip, axis=1).min() for p in lines])
    order = np.argsort(near)
    hero = max(order[:30], key=lambda i: lines[i][:, 1].max() - 3 * near[i])
    rest = [i for i in order if i != hero]
    n = min(FIBRES - 1, len(rest))
    pick = [hero] + rest[:60] + list(rng.choice(rest[60:], max(0, n - 60), replace=False))
    out = []
    for i in pick:
        p = lines[i]
        s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
        t = np.linspace(0, 1, POINTS) * s[-1]
        p = np.c_[[np.interp(t, s, p[:, k]) for k in range(3)]].T
        for _ in range(6):                 # tractography is jagged: ease the corners, keep the ends
            p[1:-1] = (p[:-2] + 2 * p[1:-1] + p[2:]) / 4
        out.append(q(p))
    return out


# the view the story ends on: story.js takes it from the data, and the brain is drawn for it here
VIEW = {'target': [-4, -14, 14], 'dist': 310, 'az': 150, 'el': 14}


SMOOTH, SULCUS = 60, (0.58, 0.78)


def brain(path, out, size=1500):
    """A pen drawing of the template's cortex as seen in VIEW, written to `out` as ink on nothing
    (black with an alpha channel): an outline, a line around each fold, and hatching for tone. Returns the half-width of the picture in the units of the view (x / depth)."""
    m = sio.loadmat(str(path))
    V, F, depth, side = [], [], [], []
    for h in ('lh', 'rh'):
        v, f = m[f'Vertices_{h}'].astype(float), m[f'Faces_{h}'].astype(int) - 1
        # drawn simply: the folds evened out, so each gyrus is one calm form and not a crinkled one
        v = np.asarray(pv.PolyData(v, np.c_[np.full(len(f), 3), f].ravel()).smooth_taubin(n_iter=SMOOTH, pass_band=0.004).points, float)
        # how deep a vertex lies under the hemisphere's hull: the hull is how far the cortex reaches
        # from the middle of the hemisphere in every direction, smoothed
        c = (v.min(0) + v.max(0)) / 2
        d = v - c
        r = np.linalg.norm(d, axis=1)
        rows, cols = 60, 120
        i = np.minimum(rows, np.round(np.arccos(np.clip(d[:, 1] / r, -1, 1)) / np.pi * rows).astype(int))
        j = np.round((np.arctan2(d[:, 2], d[:, 0]) % (2 * np.pi)) / (2 * np.pi) * cols).astype(int) % cols
        g = np.zeros((rows + 1, cols))
        np.maximum.at(g, (i, j), r)
        for _ in range(3):
            g = np.maximum(g, (np.roll(g, 1, 1) + np.roll(g, -1, 1)) / 2)
            g[1:-1] = np.maximum(g[1:-1], (g[:-2] + g[2:]) / 2)
        depth.append(np.clip(g[i, j] - r, 0, None))
        F.append(f + sum(len(x) for x in V))
        side.append(np.full(len(f), len(V)))
        V.append(v)
    V, F, depth, side = np.vstack(V), np.vstack(F), np.concatenate(depth), np.concatenate(side)
    az, el = np.radians(VIEW['az']), np.radians(VIEW['el'])
    T = np.array(VIEW['target'], float)
    E = T + VIEW['dist'] * np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    fw = (T - E) / np.linalg.norm(T - E)
    R = np.cross(fw, [0, 0, 1]); R /= np.linalg.norm(R)
    U = np.cross(R, fw)
    d = V - E
    pz = d @ fw
    xy = np.c_[d @ R / pz, d @ U / pz]
    half = float(np.abs(xy).max() * 1.04)
    A, B, C = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    n = np.cross(B - A, C - A)
    n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
    cen = (A + B + C) / 3
    to_eye = E - cen
    to_eye /= np.linalg.norm(to_eye, axis=1)[:, None]
    nv = (n * to_eye).sum(1)
    if np.median(nv[(cen - T) @ fw < 0]) < 0:        # the faces are wound the other way round
        n, nv = -n, -nv
    light = R * -0.7 + U * 0.62 - fw * 0.36           # from the upper left, towards the eye
    lam = np.clip(n @ (light / np.linalg.norm(light)), 0, 1)
    deep = np.clip(depth[F].mean(1) / 9, 0, 1)
    zf = pz[F].mean(1)

    def pen(hemis, deep=deep, nv=nv, lam=lam):
        keep = np.flatnonzero((nv > 0) & np.isin(side, hemis))
        keep = keep[np.argsort(-zf[keep])]                # far to near
        S = size * 2
        px = np.c_[(xy[:, 0] / half + 1) * S / 2, (1 - xy[:, 1] / half) * S / 2]
        val = {'deep': deep, 'nv': nv, 'lam': lam, 'z': zf, 'a': np.ones(len(F))}
        ims = {k: Image.new('F', (S, S), 0) for k in val}
        dr = {k: ImageDraw.Draw(im) for k, im in ims.items()}
        for k in keep:
            pts = [tuple(px[F[k, 0]]), tuple(px[F[k, 1]]), tuple(px[F[k, 2]])]
            for name in val:
                dr[name].polygon(pts, fill=float(val[name][k]))
        deep, nv, lam, z, a = (np.asarray(ims[k], float) for k in ('deep', 'nv', 'lam', 'z', 'a'))
        # From here on it is drawn with a pen, as the lead is: lines, and hatching for tone.
        g, ndi = ndimage.gaussian_filter, ndimage

        def ss(x, lo, hi):
            t = np.clip((x - lo) / (hi - lo), 0, 1)
            return t * t * (3 - 2 * t)

        def line(mask, width):
            return g((mask & ~ndi.binary_erosion(mask, iterations=width)).astype(float), 1.0)

        soft = g(a, 2.5)
        inside = soft > 0.5
        outline = line(inside, 5)
        # where one fold stands in front of another: a jump in the distance from the eye
        core = ndi.binary_erosion(inside, iterations=7)
        zs = np.where(inside, z, z[inside].max())
        occl = g(((ndi.maximum_filter(zs, 5) - ndi.minimum_filter(zs, 5) > 2.6) & core).astype(float), 1.3)
        # the sulci: one stroke of the pen along each, heavy in the middle and running out to nothing
        dp = g(deep, 6)
        stroke = ss(g(ss(dp, *SULCUS), 2.5), 0.45, 0.6) * inside
        # tone: only where the form turns away from the eye or from the light, in one set of lines that
        # swell into the dark and bend a little with the form; the lit faces stay paper
        tone = g(0.85 * (1 - np.clip(nv, 0, 1)) ** 1.6 + 0.5 * (1 - lam) ** 2, 9) * inside
        yy, xx = np.mgrid[0:S, 0:S]
        mm = S / 2 / half / VIEW['dist']                     # pixels to a millimetre
        zb = g(np.where(inside, z, np.nan_to_num(z[inside].mean())), 12) * mm
        period = 20
        t = ((xx * np.cos(np.radians(58)) + yy * np.sin(np.radians(58)) + 0.25 * zb) % period) - period / 2
        tint = np.clip(3.4 * ss(tone, 0.38, 0.95) - np.abs(t) + 0.5, 0, 1) * ndi.binary_erosion(inside, iterations=4)
        gy, gx = np.gradient(g(a, 6))
        weight = 0.6 + 0.4 * ss(gx * 0.7 + gy * 0.7, -0.01, 0.01)   # the outline is heavier away from the light
        return [np.maximum.reduce([outline * weight, occl * 0.6, stroke * 0.8]), tint * 0.5, g(a, 1.5)]

    # the sheets side by side, so the page can lay them one after another: the lines, the tone, the whole
    # form (the veil the cortex lays over what is inside it), and the far hemisphere drawn alone (its
    # inner wall is what stands behind the fibres when the near one is seen through)
    front, far = pen([0, 1]), pen([1])
    sheets = front + [np.maximum(far[0] * 0.8, far[1])]
    rgba = np.zeros((size, size * len(sheets), 4), np.uint8)
    for i, ink in enumerate(sheets):
        img = Image.fromarray(np.round(np.clip(ink, 0, 1) * 255).astype(np.uint8)).resize((size, size), Image.LANCZOS)
        rgba[:, i * size:(i + 1) * size, 3] = np.asarray(img)
    Image.fromarray(rgba, 'RGBA').save(out)
    return half


def cortex(path, faces=2600, smooth=140):
    """The cortex as two small, calm meshes (one a hemisphere), for the page to draw itself, with the pen
    it draws the nuclei with: the folds evened out until each gyrus is one form."""
    m = sio.loadmat(str(path))
    out = []
    for h in ('lh', 'rh'):
        v, f = m[f'Vertices_{h}'].astype(float), m[f'Faces_{h}'].astype(int) - 1
        mesh = pv.PolyData(v, np.c_[np.full(len(f), 3), f].ravel()).smooth_taubin(n_iter=smooth, pass_band=0.004)
        mesh = mesh.decimate(1 - faces / mesh.n_cells).clean().triangulate()
        mesh = mesh.smooth_taubin(n_iter=20, pass_band=0.05)
        v, f = np.asarray(mesh.points, float), mesh.faces.reshape(-1, 4)[:, 1:]
        a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
        if np.einsum('ij,ij->i', a, np.cross(b, c)).sum() < 0:   # wound so the normals point outwards
            f = f[:, ::-1]
        out.append({'v': q(v), 'f': f.ravel().tolist()})
    return out


# the axes of the two hypothetical leads (capsule, accumbens), from the front and above; story.js draws
# them along these
AXES = [[-0.36, 0.42, 0.83], [-0.2, 0.52, 0.83]]


def entries(path, lds, targets):
    """How far up each lead's axis, from the centre of its lowest contact, it passes out through the
    cortex (mm): there the page marks the entry and draws the shaft in front of the brain."""
    m = sio.loadmat(str(path))
    v, f = m['Vertices_lh'].astype(float), m['Faces_lh'].astype(int) - 1
    cortex = pv.PolyData(v, np.c_[np.full(len(f), 3), f].ravel())
    L = lds[0]
    rays = [(np.array(L['origin']) * UNIT, np.array(L['axis']))]
    for c, ax in zip(targets, AXES):
        ax = np.array(ax) / np.linalg.norm(ax)
        rays.append((np.array(c) * UNIT - ax * 3 * L['pitch'] / 2, ax))
    out = []
    for o, ax in rays:
        pts, _ = cortex.ray_trace(o, o + ax * 200)
        out.append(round(float(np.max((np.asarray(pts) - o) @ ax)), 1) if len(pts) else 70.0)
    return out


def centre(path):
    img = nib.load(str(path))
    ijk = np.argwhere(img.get_fdata() > 0.5).mean(0)
    return q((img.affine @ np.r_[ijk, 1])[:3])


def leads(path):
    reco = sio.loadmat(str(path), squeeze_me=True, struct_as_record=False)['reco']
    props = reco.props[0] if hasattr(reco.props, '__len__') else reco.props
    out, first = [], None
    for side in (1, 0):           # the left hemisphere first
        c = np.array(reco.mni.coords_mm[side], float)
        if len(c) != 8:
            raise SystemExit('story.py: expected leads with eight contacts (1-3-3-1)')
        levels = np.array([c[0], c[1:4].mean(0), c[4:7].mean(0), c[7]])
        axis = levels[-1] - levels[0]
        pitch = np.linalg.norm(axis) / 3
        axis /= np.linalg.norm(axis)
        # where the first segment of the lower ring faces, across the axis
        face = c[1] - levels[1]
        face -= axis * (face @ axis)
        face /= np.linalg.norm(face)
        first = levels if first is None else first
        out.append({
            'model': str(props.elmodel),
            'origin': q(levels[0]),            # the centre of the lowest contact
            'axis': [round(float(x), 5) for x in axis],
            'face': [round(float(x), 5) for x in face],
            'pitch': round(float(pitch), 3),   # centre to centre, mm
            'contact': 1.5, 'diameter': 1.36, 'tip': 1.0,
            'rings': [1, 3, 3, 1],
        })
    return out, first


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('space', type=Path)
    ap.add_argument('reconstruction', type=Path)
    ap.add_argument('--out', type=Path, default=ROOT / 'assets/data/story.json')
    ap.add_argument('--brain', type=Path, default=ROOT / 'assets/images/story-brain.png')
    a = ap.parse_args()
    rng = np.random.default_rng(SEED)
    lds, levels = leads(a.reconstruction)
    at = a.space / 'atlases'
    distal, ocd = at / 'DISTAL Minimal (Ewert 2017)/lh', at / 'OCD Response Tract Atlas (Li 2020)'
    dys = at / 'Human Dysfunctome Atlas (Hollunder 2024)/lh/Sweet_Spot_OCD.nii.gz'
    data = {
        'unit': UNIT,
        'space': 'MNI152NLin2009bAsym',
        'leads': lds,
        'nuclei': [dict(surface(distal / f'{n}.nii.gz', 1500 if n == 'STN' else 700), name=n) for n in ('STN', 'GPi', 'RN')]
        + [dict(surface(ocd / f'mixed/{n}.nii.gz', 700, left=True), name=n) for n in ('Ca', 'Pu')],
        'fibres': fibres(ocd / 'midline/Tract_Target_Li_2020.mat', levels[1], rng),
        'points': POINTS,
        # where stimulation went with better (sweet) and with worse (sour) outcome in OCD: the positive and
        # the negative part of the map of the Human Dysfunctome Atlas (Hollunder 2024)
        'spots': [dict(surface(dys, 500, smooth=3, rel=0.4), name='sweet'),
                  dict(surface(dys, 500, sign=-1, smooth=3, rel=0.4), name='sour')],
        'view': dict(VIEW, half=round(brain(a.space / 'cortex/CortexHiRes.mat', a.brain), 4)),
        # the two other published OCD targets the followed fibre passes on the left: capsule and accumbens
        'alic': [centre(at / f'DBS targets (Horn 2017)/lh/OCD_{n}.nii.gz') for n in ('ALIC', 'NAc')],
        'axes': AXES,
    }
    data['cortex'] = cortex(a.space / 'cortex/CortexHiRes.mat')
    data['entry'] = entries(a.space / 'cortex/CortexHiRes.mat', lds, data['alic'])
    a.out.write_text(json.dumps(data, separators=(',', ':')) + '\n')
    print(a.out, a.out.stat().st_size, 'bytes;', len(data['fibres']), 'fibres,',
          sum(len(n['f']) // 3 for n in data['nuclei']), 'nucleus triangles')


if __name__ == '__main__':
    main()
