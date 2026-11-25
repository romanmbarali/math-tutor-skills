"""Moteur motion design « cahier » pour les vidéos de maths : PIL -> frames -> ffmpeg.

Tout ce qu'il faut pour écrire un scenes.py :  from engine import *
Voir ../SKILL.md pour la méthode et ../exemple/scenes.py pour un exemple complet.
"""
import os, re, math, random, subprocess, wave
from PIL import Image, ImageDraw, ImageFont, ImageChops
from fontTools.ttLib import TTFont
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 25
SQ = 40                       # carreau
MARGE_X = 150
X0 = 190                      # début du texte (après la marge)
X_MAX = 1860                  # bord droit utile
Y_MAX = 1000                  # bas utile (dessous : barre des chapitres)
PANEL_X = 1400                # début du panneau « pense-bête » (si utilisé, rester à gauche : x < 1360)

BLEU = (29, 72, 184); ROUGE = (208, 35, 44); VERT = (18, 129, 74); NOIR = (29, 29, 31)
GRID = (201, 214, 234); MARGE = (236, 138, 138); PAPIER = (253, 253, 251)
JAUNE = (255, 235, 59); ROSE = (255, 160, 190); VERTF = (150, 255, 90); GRIS = (150, 160, 170)

F_HAND = os.path.join(HERE, "fonts/PatrickHand.ttf")
F_CAV = os.path.join(HERE, "fonts/Caveat.ttf")
F_FALL = "/System/Library/Fonts/Supplemental/STIXGeneral.otf"
CMAP = {F_HAND: TTFont(F_HAND).getBestCmap(), F_CAV: TTFont(F_CAV).getBestCmap()}
_fc = {}


def font(kind, size):
    key = (kind, size)
    if key not in _fc:
        if kind == "cav":
            f = ImageFont.truetype(F_CAV, size)
            try: f.set_variation_by_name("Bold")
            except Exception: pass
        elif kind == "fall":
            f = ImageFont.truetype(F_FALL, size)
        else:
            f = ImageFont.truetype(F_HAND, size)
        _fc[key] = f
    return _fc[key]


def path_of(kind):
    return F_CAV if kind == "cav" else F_HAND


# ---------------------------------------------------------------- fond
def paper(chapters=None, current=None):
    im = Image.new("RGB", (W, H), PAPIER)
    d = ImageDraw.Draw(im)
    for x in range(0, W, SQ): d.line([(x, 0), (x, H)], fill=GRID, width=1)
    for y in range(0, H, SQ): d.line([(0, y), (W, y)], fill=GRID, width=1)
    d.line([(MARGE_X, 0), (MARGE_X, H)], fill=MARGE, width=3)
    im = im.convert("RGBA")
    if chapters:
        _chapter_bar(im, chapters, current)
    return im


def _chapter_bar(im, chapters, current):
    """Barre discrète en bas : les chapitres, celui en cours en rouge et entouré."""
    d = ImageDraw.Draw(im)
    x = X0; y = 1030
    for i, c in enumerate(chapters):
        col = ROUGE if i == current else ((120, 140, 170) if (current is None or i > current) else VERT)
        ti, _ = text_img([(c, {"c": col, "k": "cav" if i == current else "hand"})], 34 if i == current else 28,
                         "cav" if i == current else "hand", col, pad=2)
        ty = y - ti.size[1] // 2
        if i == current:
            d.rounded_rectangle([x - 10, ty - 2, x + ti.size[0] + 10, ty + ti.size[1] + 2], 14,
                                fill=(255, 245, 200, 255), outline=ROUGE + (255,), width=3)
        im.alpha_composite(ti, (x, ty))
        x += ti.size[0] + 26
        if i < len(chapters) - 1:
            d.line([(x - 18, y), (x - 6, y)], fill=(170, 180, 200, 255), width=2)
            x += 8


# ---------------------------------------------------------------- texte riche
_TOK = re.compile(r"(_\{[^}]*\}|\^\{[^}]*\}|_\w|\^[\w\-−+*]|\*\*)")


def _runs(text, kind):
    """Découpe en runs (texte, mode, fontkind).  mode : None | 'sub' | 'sup'.
    x_1, x_{12} -> indice ;  x^2, e^{-x} -> exposant.  Glyphe absent -> police de secours (STIX)."""
    out = []
    for part in _TOK.split(text):
        if not part or part == "**": continue
        mode = None
        if part.startswith("_") and len(part) > 1 and part != "_":
            mode, part = "sub", part[2:-1] if part.startswith("_{") else part[1:]
        elif part.startswith("^") and len(part) > 1:
            mode, part = "sup", part[2:-1] if part.startswith("^{") else part[1:]
        buf, bk = "", None
        for ch in part:
            k = kind if (ord(ch) in CMAP[path_of(kind)] or ch == " ") else "fall"
            if bk is not None and k != bk:
                out.append((buf, mode, bk)); buf = ""
            buf += ch; bk = k
        if buf: out.append((buf, mode, bk))
    return out


def text_img(segs, size=44, kind="hand", color=BLEU, pad=6):
    """segs : str ou liste de (texte, {c: couleur, k: 'hand'|'cav', b: gras, s: taille}).
    -> (image RGBA, boîtes (x0,y0,x1,y1) de chaque segment, relatives à l'image)."""
    if isinstance(segs, str): segs = [(segs, {})]
    segs = [(s, {}) if isinstance(s, str) else s for s in segs]
    pieces = []
    x = pad; boxes = []
    asc = font(kind, size).getmetrics()[0]
    for txt, st in segs:
        k = st.get("k", kind); sz = st.get("s", size); col = st.get("c", color); b = st.get("b", False)
        x0 = x
        for run, mode, rk in _runs(txt, k):
            fsz = int(sz * 0.62) if mode else sz
            f = font(rk, fsz if rk != "fall" else int(fsz * 0.92))
            fa = f.getmetrics()[0]
            if mode == "sub": baseline = asc + pad + int(sz * 0.20)
            elif mode == "sup": baseline = asc + pad - int(sz * 0.36)
            else: baseline = asc + pad
            if rk == "fall": baseline += int(sz * 0.04)
            pieces.append((x, run, f, col, b, baseline - fa))
            x += f.getlength(run) + (1 if b else 0)
        boxes.append((x0, x))
    # Caveat penche à droite : la dernière lettre déborde de getlength -> marge en plus
    over = int(size * 0.18) if any(st.get("k", kind) == "cav" for _, st in segs) else 0
    w = int(x + pad + over); h = int(size * 1.45 + pad)
    im = Image.new("RGBA", (max(w, 2), h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for (px, run, f, col, b, py) in pieces:
        d.text((px, py), run, font=f, fill=col + (255,),
               stroke_width=1 if b else 0, stroke_fill=col + (255,))
    boxes = [(a, pad + int(size * 0.12), bb, pad + int(size * 1.22)) for a, bb in boxes]
    return im, boxes


# ---------------------------------------------------------------- éléments
class El:
    """Un élément posé sur la page. t0 (début d'apparition) est calculé par render.py."""
    def __init__(self, img, x, y, anim="wipe", dur=0.6):
        self.img, self.x, self.y, self.anim, self.dur = img, int(x), int(y), anim, dur
        self.t0 = 0.0; self.blend = "over"; self.t_off = 0.0
        self.w, self.h = img.size
        self.is_text = False

    @property
    def right(self): return self.x + self.w
    @property
    def bottom(self): return self.y + self.h
    @property
    def box(self): return (self.x, self.y, self.right, self.bottom)
    @property
    def cy(self): return self.y + self.h // 2

    def move(self, dx, dy):
        dx, dy = int(dx), int(dy)
        self.x += dx; self.y += dy
        if hasattr(self, "boxes"): self.boxes = [(a + dx, b + dy, c + dx, d + dy) for a, b, c, d in self.boxes]
        if hasattr(self, "cells"): self.cells = {k: (a + dx, b + dy, c + dx, d + dy) for k, (a, b, c, d) in self.cells.items()}
        if hasattr(self, "colx"): self.colx = [c + dx for c in self.colx]
        return self

    def frame(self, p):
        """-> (img, x, y) pour la progression p in [0,1]."""
        e = 1 - (1 - p) ** 3
        if self.anim == "wipe":
            w = max(1, int(self.w * e))
            return self.img.crop((0, 0, w, self.h)), self.x, self.y
        if self.anim == "fade":
            im = self.img.copy(); a = im.getchannel("A").point(lambda v: int(v * e)); im.putalpha(a)
            return im, self.x, self.y
        if self.anim == "rise":
            im = self.img.copy(); a = im.getchannel("A").point(lambda v: int(v * e)); im.putalpha(a)
            return im, self.x, self.y + int((1 - e) * 30)
        if self.anim == "pop":
            if p >= 1: return self.img, self.x, self.y
            s = max(0.3, min(1.12, 0.5 + 0.6 * e - 0.1 * (e ** 4)))
            nw, nh = max(1, int(self.w * s)), max(1, int(self.h * s))
            im = self.img.resize((nw, nh), Image.LANCZOS)
            a = im.getchannel("A").point(lambda v: int(v * min(1, e * 1.5))); im.putalpha(a)
            return im, self.x + (self.w - nw) // 2, self.y + (self.h - nh) // 2
        return self.img, self.x, self.y


class Stroke(El):
    """Polyline dessinée progressivement (cadres, soulignés, flèches, cercles, ratures)."""
    def __init__(self, pts_list, color, width, dur=0.8):
        xs = [p[0] for pts in pts_list for p in pts]; ys = [p[1] for pts in pts_list for p in pts]
        self.ox, self.oy = int(min(xs)) - width * 2, int(min(ys)) - width * 2
        w = int(max(xs) - self.ox + width * 2); h = int(max(ys) - self.oy + width * 2)
        self.pts_list = [[(px - self.ox, py - self.oy) for px, py in pts] for pts in pts_list]
        self.color, self.width = color, width
        super().__init__(Image.new("RGBA", (max(w, 2), max(h, 2))), self.ox, self.oy, "stroke", dur)
        self.full = self._draw(1.0)

    def _draw(self, p):
        im = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        segs = []
        for pts in self.pts_list:
            for a, b in zip(pts, pts[1:]): segs.append((a, b, math.dist(a, b)))
        tot = sum(s[2] for s in segs); left = tot * p
        for a, b, L in segs:
            if left <= 0: break
            if L > left:
                t = left / L; b = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            d.line([a, b], fill=self.color + (255,), width=self.width, joint="curve")
            left -= L
        return im

    def frame(self, p):
        if p >= 1: return self.full, self.x, self.y
        return self._draw(1 - (1 - p) ** 2), self.x, self.y


def hand_rect(x0, y0, x1, y1, seed=1, j=5):
    r = random.Random(seed)
    def jit(): return r.uniform(-j, j)
    pts = []
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    for (a, b) in zip(corners, corners[1:]):
        for i in range(12):
            t = i / 12
            pts.append((a[0] + (b[0] - a[0]) * t + jit() * 0.4, a[1] + (b[1] - a[1]) * t + jit() * 0.4))
    pts.append((x0 + 18, y0 + jit()))
    return pts


def _bx(o):
    """El, ou boîte (x0,y0,x1,y1) -> boîte."""
    return o.box if isinstance(o, El) else o


# ---------------------------------------------------------------- composants
def T(segs, x, y, size=44, kind="hand", color=BLEU, anim="wipe", dur=None):
    """Ligne de texte. segs : str ou [(texte, style)]. Indices x_1 / x_{ij}, exposants x^2 / e^{-t}.
    e.boxes[i] = boîte du segment i (pour highlight / circle / strike)."""
    im, boxes = text_img(segs, size, kind, color)
    e = El(im, x, y, anim, dur if dur is not None else min(1.4, 0.25 + im.size[0] / 1400))
    e.boxes = [(x + a, y + b, x + c, y + d) for a, b, c, d in boxes]
    e.is_text = True
    return e


def title(txt, y=40, size=96):
    e = T([(txt, {"k": "cav", "c": ROUGE})], X0, y, size=size, kind="cav", anim="wipe", dur=0.9)
    u = Stroke([[(e.x + 8, e.bottom - 18), (e.right - 10, e.bottom - 22)]], ROUGE, 4, dur=0.5)
    return [e, u]


def h3(txt, x=X0, y=0, size=64):
    return T([("▸ ", {"k": "fall", "c": ROUGE, "s": int(size * 0.6)}), (txt, {"k": "cav", "c": ROUGE})],
             x, y, size=size, kind="cav", dur=0.8)


def side(txt, x, y, size=50, color=VERT):
    """Petite remarque manuscrite (Caveat vert), ex. « ← 3 × (−1) = −3 »."""
    return T([(txt, {"k": "cav", "c": color})], x, y, size=size, kind="cav")


def highlight(box, color=JAUNE, dur=0.5, pad=4):
    """Surligneur (multiplicatif). box : El ou (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = _bx(box)
    im = Image.new("RGBA", (int(x1 - x0 + 2 * pad), int(y1 - y0)), color + (255,))
    e = El(im, x0 - pad, y0, "wipe", dur); e.blend = "multiply"
    return e


def frame_box(el_or_box, color=ROUGE, pad=16, seed=3, dur=0.8, width=4):
    """Cadre rouge à la main (résultat final)."""
    b = _bx(el_or_box)
    return Stroke([hand_rect(b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad, seed)], color, width, dur)


def circle(el_or_box, color=ROUGE, pad=12, seed=4, dur=0.6, width=4):
    """Entoure à la main (ellipse un peu tremblée, qui dépasse légèrement)."""
    x0, y0, x1, y1 = _bx(el_or_box)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; rx, ry = (x1 - x0) / 2 + pad, (y1 - y0) / 2 + pad
    r = random.Random(seed); pts = []
    for i in range(0, 64):
        a = -math.pi * 0.75 + i / 56 * 2 * math.pi
        k = 1 + r.uniform(-0.03, 0.03)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return Stroke([pts], color, width, dur)


def underline(el_or_box, color=ROUGE, dur=0.4, width=4, wavy=False):
    x0, y0, x1, y1 = _bx(el_or_box)
    if wavy:
        pts = [(x, y1 + 4 + 5 * math.sin((x - x0) / 9)) for x in range(int(x0), int(x1), 4)]
    else:
        pts = [(x0, y1 + 2), (x1, y1 - 2)]
    return Stroke([pts], color, width, dur)


def strike(el_or_box, color=ROUGE, dur=0.35, width=4):
    """Barre en diagonale (termes qui s'annulent, faux résultat)."""
    x0, y0, x1, y1 = _bx(el_or_box)
    return Stroke([[(x0 - 2, y1 - 6), (x1 + 2, y0 + 8)]], color, width, dur)


def arrow(p0, p1, color=ROUGE, width=4, dur=0.6, bend=0.18):
    """Flèche courbe à la main de p0 vers p1."""
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0)
    cx, cy = mx + nx * bend, my + ny * bend
    pts = [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1)
           for t in [i / 30 for i in range(31)]]
    ang = math.atan2(y1 - pts[-4][1], x1 - pts[-4][0]); L = 22
    head = [(x1 - L * math.cos(ang - 0.45), y1 - L * math.sin(ang - 0.45)), (x1, y1),
            (x1 - L * math.cos(ang + 0.45), y1 - L * math.sin(ang + 0.45))]
    return Stroke([pts, head], color, width, dur)


def card(x, y, w, h, kind="note", title_txt=None, dur=0.6):
    """Cadre : 'note' (rappel, vert pointillé), 'piege' (rouge), 'oral' (post-it jaune)."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind == "note":
        d.rounded_rectangle([2, 2, w - 3, h - 3], 16, fill=(255, 255, 255, 190))
        def dash(a, b):
            L = math.dist(a, b); n = max(1, int(L // 22))
            for i in range(n):
                t0, t1 = i / n, (i + 0.55) / n
                d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                        (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=VERT + (255,), width=4)
        for a, b in [((4, 4), (w - 4, 4)), ((w - 4, 4), (w - 4, h - 4)), ((w - 4, h - 4), (4, h - 4)), ((4, h - 4), (4, 4))]:
            dash(a, b)
        tc = VERT
    elif kind == "piege":
        d.rounded_rectangle([2, 2, w - 3, h - 3], 18, fill=(255, 238, 238, 235), outline=ROUGE + (255,), width=4)
        tc = ROUGE
    else:  # oral
        d.rectangle([8, 8, w - 1, h - 1], fill=(0, 0, 0, 30))
        d.rectangle([0, 0, w - 9, h - 9], fill=(255, 248, 196, 255), outline=NOIR + (255,), width=3)
        tc = NOIR
    if title_txt:
        ti, _ = text_img([(title_txt, {"k": "cav", "c": tc})], 54, "cav")
        im.alpha_composite(ti, (20, 4))
    return El(im, x, y, "rise", dur)


def memo(title_txt, lines, x=PANEL_X, y=170, w=None, size=38, color=NOIR):
    """Panneau « pense-bête » à droite, qui reste affiché : l'énoncé, les résultats déjà trouvés…
    lines : liste de segs (str ou [(txt, style)]). Retourne [cadre, ligne1, ligne2, ...]."""
    w = w or (X_MAX - x)
    gap = int(size * 1.35)
    h = 80 + gap * len(lines) + 10
    c = card(x, y, w, h, "note", title_txt, dur=0.4)
    els = [c]
    for i, l in enumerate(lines):
        els.append(T(l, x + 24, y + 70 + i * gap, size=size, color=color, anim="fade", dur=0.3))
    return els


def matrix(rows, x, y, size=50, color=BLEU, colw=None, bar=None, cell_bg=None, gap=26, rowh=None, cell_col=None):
    """Matrice entre parenthèses. rows : liste de listes de str. bar : colonne avant laquelle tracer
    la barre (matrice augmentée). e.cells[(i, j)] = boîte de la case (pour highlight / circle)."""
    ncol = len(rows[0]); nrow = len(rows)
    imgs = [[text_img(c, size, "hand", (cell_col or {}).get((i, j), color), pad=2)[0] for j, c in enumerate(r)] for i, r in enumerate(rows)]
    cw = [max(imgs[i][j].size[0] for i in range(nrow)) for j in range(ncol)]
    if colw: cw = [max(c, colw) for c in cw]
    rh = rowh or int(size * 1.25)
    par = 26
    w = par * 2 + sum(cw) + gap * (ncol - 1) + 20 + (24 if bar else 0)
    h = rh * nrow + 24
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx = par + 10; centers = []
    for j in range(ncol):
        if bar is not None and j == bar:
            d.line([(cx - gap // 2 + 6, 14), (cx - gap // 2 + 6, h - 14)], fill=color + (255,), width=4); cx += 24
        centers.append(cx + cw[j] / 2); cx += cw[j] + gap
    cellboxes = {}
    for i in range(nrow):
        for j in range(ncol):
            ci = imgs[i][j]
            px = int(centers[j] - ci.size[0] / 2); py = 12 + i * rh + (rh - ci.size[1]) // 2 + 4
            cellboxes[(i, j)] = (x + int(centers[j] - cw[j] / 2) - 6, y + 12 + i * rh + 4, x + int(centers[j] + cw[j] / 2) + 6, y + 12 + (i + 1) * rh)
            if cell_bg and (i, j) in cell_bg:
                b = cellboxes[(i, j)]
                d.rounded_rectangle([b[0] - x, b[1] - y, b[2] - x, b[3] - y], 8, fill=cell_bg[(i, j)] + (150,))
            im.alpha_composite(ci, (px, py))
    for side_ in (0, 1):
        pts = []
        for k in range(31):
            t = k / 30; yy = 6 + t * (h - 12)
            xx = 14 * (1 - math.sin(t * math.pi)) + 6
            pts.append((xx if side_ == 0 else w - xx, yy))
        d.line(pts, fill=color + (255,), width=4, joint="curve")
    e = El(im, x, y, "wipe", 0.7)
    e.cells = cellboxes
    return e


def frac(num, den, x=0, y=0, size=48, color=BLEU):
    """Fraction : num / den (segs) avec barre. À aligner avec row()."""
    a, _ = text_img(num, size, "hand", color, pad=2); b, _ = text_img(den, size, "hand", color, pad=2)
    w = max(a.size[0], b.size[0]) + 16
    h = a.size[1] + b.size[1] + 10
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    im.alpha_composite(a, ((w - a.size[0]) // 2, 0))
    ly = a.size[1] + 3
    d.line([(4, ly), (w - 4, ly)], fill=color + (255,), width=3)
    im.alpha_composite(b, ((w - b.size[0]) // 2, ly + 5))
    return El(im, x, y, "wipe", 0.6)


def row(els, x, cy, gap=10):
    """Aligne des éléments (T, frac, matrix…) côte à côte, centrés verticalement sur cy.
    Permet de faire apparaître un calcul morceau par morceau. Retourne la liste."""
    for e in els:
        e.move(x - e.x, cy - e.h // 2 - e.y)
        x = e.right + gap
    return els


def system(lines, x, y, size=50, color=NOIR, gap=None):
    """Système avec accolade. Retourne [accolade, ligne1, ligne2, ...]."""
    gap = gap or int(size * 1.35)
    els = []
    for i, l in enumerate(lines):
        els.append(T(l, x + 46, y + i * gap, size=size, color=color))
    hgt = gap * len(lines) + 10
    br, _ = text_img([("{", {"k": "cav", "c": color})], int(hgt * 0.95), "cav", color, pad=0)
    b = El(br.resize((int(br.size[0] * 0.7), br.size[1])), x - 10, y - int(hgt * 0.22), "fade", 0.4)
    return [b] + els


def table(rows, x, y, size=40, colw=None, header=True, cell_col=None, rowh=None):
    """Tableau bleu. Retourne une liste d'El, une par ligne (pour les faire apparaître une à une)."""
    ncol = len(rows[0]); rh = rowh or int(size * 1.55)
    imgs = []
    for i, r in enumerate(rows):
        ri = []
        for j, c in enumerate(r):
            kind = "cav" if (header and i == 0) else "hand"
            col = ROUGE if (header and i == 0) else (cell_col or {}).get((i, j), BLEU)
            sz = int(size * 1.15) if kind == "cav" else size
            ri.append(text_img([(c, {"k": kind, "c": col})] if isinstance(c, str) else c, sz, kind, col, pad=2)[0])
        imgs.append(ri)
    cw = [max(imgs[i][j].size[0] for i in range(len(rows))) + 34 for j in range(ncol)]
    if colw: cw = [max(a, b) for a, b in zip(cw, colw)]
    W_ = sum(cw); out = []
    for i, r in enumerate(imgs):
        im = Image.new("RGBA", (W_ + 4, rh + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        cx = 0
        for j, ci in enumerate(r):
            d.rectangle([cx, 0, cx + cw[j], rh], outline=BLEU + (255,), width=3)
            im.alpha_composite(ci, (int(cx + (cw[j] - ci.size[0]) / 2), int((rh - ci.size[1]) / 2) + 3))
            cx += cw[j]
        e = El(im, x, y + i * rh, "wipe", 0.6)
        e.colx = [x + sum(cw[:j]) for j in range(ncol + 1)]
        e.cells = {j: (e.colx[j], y + i * rh, e.colx[j + 1], y + (i + 1) * rh) for j in range(ncol)}
        out.append(e)
    return out


def num(n, x, y, size=40):
    """Pastille de numéro d'étape (cercle rouge)."""
    s = int(size * 1.15)
    im = Image.new("RGBA", (s + 8, s + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([3, 3, s + 3, s + 2], outline=ROUGE + (255,), width=4)
    ti, _ = text_img([(str(n), {"k": "cav", "c": ROUGE})], int(size * 0.95), "cav", ROUGE, pad=0)
    im.alpha_composite(ti, ((s + 8 - ti.size[0]) // 2, (s + 8 - ti.size[1]) // 2 + 2))
    return El(im, x, y, "pop", 0.4)


def step(n, segs, x, y, size=44, color=BLEU):
    """[pastille n, texte]. Le texte est step(...)[1] (pour highlight(step[1].boxes[k]))."""
    c = num(n, x, y + 6, size)
    t = T(segs, x + c.w + 8, y, size=size, color=color)
    t.t_off = 0.15
    return [c, t]


# ---------------------------------------------------------------- scènes
SCENES = []


class Scene:
    """Une scène = une page. Chaque beat = une phrase dite + ce qui apparaît pendant.

    s.beat("On remplace x 4 par @a moins 1, donc x 3 vaut @b 6.", ti, ("@a", e1), ("@b", [e2, hl]))
      - un élément seul apparaît au début de la phrase ;
      - ("@nom", el)  : apparaît pile quand la voix prononce le mot qui suit @nom ;
      - (0.6, el)     : apparaît à 60 % de la phrase (approximatif, à éviter) ;
      - une liste d'éléments apparaît en cascade (0,12 s d'écart).
    gap= : silence après la phrase (défaut 0,45 s ; mettre 1.2 après un résultat important).
    """
    def __init__(self, name, chap=None):
        self.name = name; self.chap = chap; self.beats = []

    def beat(self, say, *items, gap=None):
        out = []
        for it in items:
            if isinstance(it, tuple): fr, obj = it
            else: fr, obj = 0.0, it
            objs = obj if isinstance(obj, list) else [obj]
            flat = []
            for o in objs:
                flat.extend(o if isinstance(o, list) else [o])
            for k, o in enumerate(flat):
                out.append((fr, k * 0.12, o))
        self.beats.append((say, out, gap))
        return self

    def pause(self, sec=1.0):
        """Silence (laisse le temps de lire / regarder)."""
        self.beats.append((None, [], sec))
        return self


def S(name, chap=None):
    """Nouvelle scène. name : '03_q1_tableau' (l'ordre alphabétique = l'ordre du film). chap : index dans CHAPTERS."""
    sc = Scene(name, chap); SCENES.append(sc); return sc


# ---------------------------------------------------------------- rendu
def _put(canvas, e, p):
    im, x, y = e.frame(p)
    if e.blend == "multiply":
        region = canvas.crop((x, y, x + im.size[0], y + im.size[1]))
        tint = Image.new("RGBA", im.size, (255, 255, 255, 255)); tint.alpha_composite(im)
        mixed = Image.blend(Image.new("RGBA", im.size, (255, 255, 255, 255)), tint, 0.55)
        canvas.paste(ImageChops.multiply(region, mixed), (x, y))
    else:
        if x < 0 or y < 0:
            canvas.alpha_composite(im.crop((max(0, -x), max(0, -y), im.size[0], im.size[1])), (max(0, x), max(0, y)))
        else:
            canvas.alpha_composite(im, (x, y))


def render_scene(els, total, audio_wav, out_mp4, bg, fade_out=0.35, scale=1.0):
    els = sorted(els, key=lambda e: e.t0)
    base = bg.copy(); baked = set()
    n = int(math.ceil(total * FPS))
    ow, oh = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}", "-r", str(FPS),
           "-i", "-", "-i", audio_wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", out_mp4]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(n):
        t = fi / FPS
        for i, e in enumerate(els):
            if i in baked: continue
            if t >= e.t0 + e.dur and all(j in baked for j in range(i)):
                _put(base, e, 1.0); baked.add(i)
        frame = base.copy()
        for i, e in enumerate(els):
            if i in baked or t < e.t0: continue
            _put(frame, e, min(1.0, (t - e.t0) / e.dur))
        if t > total - fade_out:
            a = (t - (total - fade_out)) / fade_out
            frame = Image.blend(frame, bg, min(1, a))
        fr = frame.convert("RGB")
        if scale != 1.0: fr = fr.resize((ow, oh), Image.BILINEAR)
        pr.stdin.write(fr.tobytes())
    pr.stdin.close(); pr.wait()


def still(els, t, path, bg):
    """Image de contrôle à l'instant t."""
    fr = bg.copy()
    for e in sorted(els, key=lambda e: e.t0):
        if t >= e.t0:
            _put(fr, e, min(1.0, (t - e.t0) / e.dur))
    fr.convert("RGB").save(path)


def check_layout(name, els):
    """Avertit si un texte sort de la zone utile ou en chevauche un autre."""
    warn = []
    for e in els:
        if isinstance(e, Stroke) or e.blend == "multiply": continue
        if e.right > X_MAX + 30 or e.bottom > Y_MAX + 20 or e.x < MARGE_X:
            warn.append(f"{name}: hors cadre {e.box}")
    txt = [e for e in els if e.is_text]
    for i, a in enumerate(txt):
        for b in txt[i + 1:]:
            ax0, ay0, ax1, ay1 = a.x + 6, a.y + 8, a.right - 6, a.bottom - 8
            bx0, by0, bx1, by1 = b.x + 6, b.y + 8, b.right - 6, b.bottom - 8
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                warn.append(f"{name}: chevauchement {a.box} / {b.box}")
    return warn
