"""Blueprint drawing library — pure SVG, no third-party dependency.

Every sheet produced with this library carries the same frame: cyanotype
ground, zone grid A-F x 1-8, classification band, general-notes block
(upper left), revision block (upper right), title block (lower right),
optional parts list, numbered balloons. Conventions are in
docs/blueprints/PLAN_1_BLUEPRINT_PROGRAMME.md section 4.
"""
from __future__ import annotations

import html
import math
import textwrap
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

W, H = 1600, 1000
MARGIN = 28
INNER = (MARGIN + 18, MARGIN + 18, W - MARGIN - 18, H - MARGIN - 18)  # x0 y0 x1 y1

# cyanotype palette
GROUND = "#0b2a5b"
GROUND_DK = "#071d41"
LINE = "#f2f6ff"
LINE_SOFT = "#b9c9e8"
LINE_FAINT = "#5c78ad"
ACCENT = "#ffd166"   # measured value highlight
WARN = "#ff7b7b"     # adversary / fail
OK = "#9be7a5"       # defended / pass
MONO = "DejaVu Sans Mono, Menlo, Consolas, monospace"
SANS = "DejaVu Sans, Helvetica, Arial, sans-serif"

PROGRAMME = "CVIN-SSI PROGRAMME"
BAND = "UNCLASSIFIED // THESIS RESEARCH — MEASURED"
DRAWN = "N. PRAKASH"
CHECKED = "MEASUREMENT_CONDITIONS.md"
APPROVED = "—"
DATE = "2026-10-15"
DATE_B = "2026-10-22"


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


@dataclass
class Sheet:
    number: str
    title: str
    subtitle: str = ""
    sheet_no: int = 1
    sheet_of: int = 1
    rev: str = "B"
    scale: str = "NTS"
    notes: List[str] = field(default_factory=list)
    notes_width: int = 400
    revisions: List[Tuple[str, str, str]] = field(default_factory=lambda: [("A", "INITIAL RELEASE", DATE), ("B", "P1 NUMBER AUDIT (AUDIT_REV_B.md)", DATE_B)])
    parts: List[Tuple[int, str, str]] = field(default_factory=list)  # (balloon, name, spec)
    parts_title: str = "PARTS LIST"
    parts_pos: Tuple[int, int] = (0, 0)  # 0,0 = auto (lower-left)
    parts_width: int = 540
    body: List[str] = field(default_factory=list)
    refs: List[str] = field(default_factory=list)

    # ---------------------------------------------------------------- raw
    def add(self, s: str) -> None:
        self.body.append(s)

    # --------------------------------------------------------------- text
    def text(self, x, y, s, size=13, color=LINE, anchor="start", mono=False, weight="normal",
             italic=False, opacity=1.0, rotate: Optional[float] = None, spacing=None):
        fam = MONO if mono else SANS
        tr = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
        st = ' font-style="italic"' if italic else ""
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        self.add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{color}" '
                 f'text-anchor="{anchor}" font-weight="{weight}" opacity="{opacity}"{st}{ls}{tr}>{esc(s)}</text>')

    def lines(self, x, y, items: Sequence[str], size=12, lh=None, color=LINE, mono=False, anchor="start", weight="normal"):
        lh = lh or int(size * 1.35)
        for i, s in enumerate(items):
            self.text(x, y + i * lh, s, size=size, color=color, mono=mono, anchor=anchor, weight=weight)
        return y + len(items) * lh

    def wrap(self, x, y, s, width_chars=60, size=12, lh=None, color=LINE, mono=False, anchor="start"):
        return self.lines(x, y, textwrap.wrap(s, width_chars), size=size, lh=lh, color=color, mono=mono, anchor=anchor)

    # ------------------------------------------------------------- shapes
    def rect(self, x, y, w, h, stroke=LINE, sw=2.4, fill="none", dash=None, rx=0, opacity=1.0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{sw}" opacity="{opacity}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke=LINE, sw=1.2, dash=None, opacity=1.0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"{d}/>')

    def poly(self, pts, stroke=LINE, sw=1.6, fill="none", dash=None, close=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        p = " ".join(f"{x},{y}" for x, y in pts)
        tag = "polygon" if close else "polyline"
        self.add(f'<{tag} points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, stroke=LINE, sw=1.6, fill="none"):
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def arrow(self, x1, y1, x2, y2, stroke=LINE, sw=1.6, dash=None, head=9, label=None, lsize=11, lcolor=None, loff=-6, mono=False, both=False):
        self.line(x1, y1, x2, y2, stroke=stroke, sw=sw, dash=dash)
        self._head(x1, y1, x2, y2, stroke, head)
        if both:
            self._head(x2, y2, x1, y1, stroke, head)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
            if ang > 90 or ang < -90:
                ang += 180
            self.text(mx, my + loff, label, size=lsize, color=lcolor or stroke, anchor="middle", mono=mono, rotate=ang)

    def _head(self, x1, y1, x2, y2, stroke, head):
        ang = math.atan2(y2 - y1, x2 - x1)
        a1, a2 = ang + math.radians(155), ang - math.radians(155)
        p1 = (x2 + head * math.cos(a1), y2 + head * math.sin(a1))
        p2 = (x2 + head * math.cos(a2), y2 + head * math.sin(a2))
        self.poly([p1, (x2, y2), p2], stroke=stroke, sw=1.4, fill=stroke, close=True)

    def elbow(self, x1, y1, x2, y2, stroke=LINE, sw=1.4, dash=None, head=True, via="h"):
        """orthogonal connector: via='h' goes horizontal first, 'v' vertical first."""
        if via == "h":
            mx = x2
            pts = [(x1, y1), (mx, y1), (x2, y2)]
        else:
            pts = [(x1, y1), (x1, y2), (x2, y2)]
        self.poly(pts, stroke=stroke, sw=sw, dash=dash)
        if head:
            px, py = pts[-2]
            self._head(px, py, x2, y2, stroke, 8)

    # -------------------------------------------------------------- boxes
    def box(self, x, y, w, h, title, lines_: Sequence[str] = (), sw=2.0, stroke=LINE, fill="none", tsize=13,
            bsize=11, mono_body=True, dash=None, title_color=None, pad=10, rx=0):
        self.rect(x, y, w, h, stroke=stroke, sw=sw, fill=fill, dash=dash, rx=rx)
        self.text(x + pad, y + pad + tsize, title, size=tsize, weight="bold", color=title_color or stroke)
        if lines_:
            self.line(x + 4, y + pad + tsize + 7, x + w - 4, y + pad + tsize + 7, stroke=stroke, sw=0.8, opacity=0.7)
            self.lines(x + pad, y + pad + tsize + 7 + bsize + 6, lines_, size=bsize, mono=mono_body, color=LINE_SOFT if stroke == LINE else stroke)

    def balloon(self, n: int, x, y, r=13, to: Optional[Tuple[float, float]] = None, color=ACCENT):
        if to:
            self.line(x, y, to[0], to[1], stroke=color, sw=1.0)
            self.circle(to[0], to[1], 2.5, stroke=color, fill=color)
        self.circle(x, y, r, stroke=color, sw=1.6, fill=GROUND)
        self.text(x, y + 5, str(n), size=13, color=color, anchor="middle", weight="bold")

    def dim(self, x1, y1, x2, y2, label, size=11, color=LINE_SOFT, off=0):
        """dimension line with tick ends, horizontal or vertical."""
        self.line(x1, y1, x2, y2, stroke=color, sw=0.9)
        for (x, y) in ((x1, y1), (x2, y2)):
            if y1 == y2:
                self.line(x, y - 6, x, y + 6, stroke=color, sw=0.9)
            else:
                self.line(x - 6, y, x + 6, y, stroke=color, sw=0.9)
        if y1 == y2:
            self.text((x1 + x2) / 2, y1 - 5 + off, label, size=size, color=color, anchor="middle", mono=True)
        else:
            self.text(x1 + 8 + off, (y1 + y2) / 2 + 4, label, size=size, color=color, mono=True)

    def table(self, x, y, cols: Sequence[Tuple[str, int]], rows: Sequence[Sequence[str]], size=11, lh=20,
              header=True, mono=True, stroke=LINE_SOFT, hcolor=ACCENT, cell_colors=None):
        tw = sum(w for _, w in cols)
        yy = y
        if header:
            self.rect(x, yy, tw, lh, stroke=stroke, sw=1.0, fill=GROUND_DK)
            cx = x
            for name, w in cols:
                self.text(cx + 6, yy + lh - 6, name, size=size, color=hcolor, mono=mono, weight="bold")
                cx += w
            yy += lh
        for ri, r in enumerate(rows):
            self.rect(x, yy, tw, lh, stroke=stroke, sw=0.8)
            cx = x
            for ci, (name, w) in enumerate(cols):
                val = r[ci] if ci < len(r) else ""
                col = LINE
                if cell_colors:
                    col = cell_colors(ri, ci, val) or LINE
                self.text(cx + 6, yy + lh - 6, val, size=size, color=col, mono=mono)
                cx += w
            yy += lh
        cx = x
        for name, w in cols[:-1]:
            cx += w
            self.line(cx, y, cx, yy, stroke=stroke, sw=0.8)
        return yy

    def lifeline(self, x, y0, y1, name, sub="", w=150):
        self.rect(x - w / 2, y0, w, 40, sw=1.8)
        self.text(x, y0 + 18, name, size=12, anchor="middle", weight="bold")
        if sub:
            self.text(x, y0 + 33, sub, size=10, anchor="middle", color=LINE_SOFT, mono=True)
        self.line(x, y0 + 40, x, y1, stroke=LINE_SOFT, sw=1.0, dash="6,5")

    def msg(self, x1, x2, y, n, label, dash=None, color=LINE, note=None, self_call=False, left=False):
        if self_call:
            d = -1 if left else 1
            self.poly([(x1, y), (x1 + d * 40, y), (x1 + d * 40, y + 22), (x1 + d * 6, y + 22)], stroke=color, sw=1.4, dash=dash)
            self._head(x1 + d * 40, y + 22, x1 + d * 6, y + 22, color, 8)
            self.text(x1 + d * 48, y + 16, f"{n}  {label}", size=11, color=color, mono=True, anchor="end" if left else "start")
            return y + 22
        self.arrow(x1, y, x2, y, stroke=color, sw=1.4, dash=dash)
        mid = (x1 + x2) / 2
        self.text(mid, y - 6, f"{n}  {label}", size=11, color=color, anchor="middle", mono=True)
        if note:
            self.text(mid, y + 14, note, size=10, color=LINE_SOFT, anchor="middle", italic=True)
        return y

    def activation(self, x, y0, y1, w=8, color=ACCENT):
        self.rect(x - w / 2, y0, w, y1 - y0, stroke=color, sw=1.2, fill=GROUND_DK)

    def state(self, x, y, w, h, name, sub="", stroke=LINE):
        self.rect(x, y, w, h, stroke=stroke, sw=2.0, rx=12)
        self.text(x + w / 2, y + h / 2 + (0 if sub else 5), name, size=12, anchor="middle", weight="bold", color=stroke)
        if sub:
            self.text(x + w / 2, y + h / 2 + 15, sub, size=10, anchor="middle", color=LINE_SOFT, mono=True)

    def section_label(self, x, y, s, color=LINE_SOFT):
        self.text(x, y, s, size=11, color=color, weight="bold", spacing=2)
        self.line(x, y + 5, x + len(s) * 8.5, y + 5, stroke=color, sw=0.9)

    def hatch_rect(self, x, y, w, h, stroke=LINE_FAINT, step=9):
        self.rect(x, y, w, h, stroke=stroke, sw=1.0)
        self.add(f'<clipPath id="hc{abs(hash((x, y, w, h)))}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>')
        cid = f"hc{abs(hash((x, y, w, h)))}"
        self.add(f'<g clip-path="url(#{cid})">')
        for i in range(-h, w, step):
            self.line(x + i, y + h, x + i + h, y, stroke=stroke, sw=0.6)
        self.add("</g>")

    # ------------------------------------------------------------ frame
    def _frame(self) -> str:
        out = []
        x0, y0, x1, y1 = INNER
        out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
        out.append(f'<title>{esc(self.number)} — {esc(self.title)}</title>')
        out.append('<defs>'
                   f'<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">'
                   f'<path d="M 40 0 L 0 0 0 40" fill="none" stroke="{LINE_FAINT}" stroke-width="0.35" opacity="0.55"/></pattern>'
                   f'<pattern id="grid2" width="200" height="200" patternUnits="userSpaceOnUse">'
                   f'<path d="M 200 0 L 0 0 0 200" fill="none" stroke="{LINE_FAINT}" stroke-width="0.7" opacity="0.6"/></pattern>'
                   '</defs>')
        out.append(f'<rect width="{W}" height="{H}" fill="{GROUND}"/>')
        out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#grid)"/>')
        out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#grid2)"/>')
        # outer border + inner border
        out.append(f'<rect x="{MARGIN}" y="{MARGIN}" width="{W - 2 * MARGIN}" height="{H - 2 * MARGIN}" fill="none" stroke="{LINE}" stroke-width="2.6"/>')
        out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="none" stroke="{LINE}" stroke-width="1.2"/>')
        # zones: numbers 1-8 horizontal, letters A-F vertical
        nz, nl = 8, 6
        zw = (x1 - x0) / nz
        zh = (y1 - y0) / nl
        for i in range(nz):
            cx = x0 + zw * (i + 0.5)
            for yy in (MARGIN + 13, H - MARGIN - 5):
                out.append(f'<text x="{cx}" y="{yy}" font-family="{MONO}" font-size="11" fill="{LINE_SOFT}" text-anchor="middle">{nz - i}</text>')
            if 0 < i:
                for (ya, yb) in ((MARGIN, y0), (y1, H - MARGIN)):
                    out.append(f'<line x1="{x0 + zw * i}" y1="{ya}" x2="{x0 + zw * i}" y2="{yb}" stroke="{LINE_SOFT}" stroke-width="0.8"/>')
        for j in range(nl):
            cy = y0 + zh * (j + 0.5) + 4
            for xx in (MARGIN + 9, W - MARGIN - 9):
                out.append(f'<text x="{xx}" y="{cy}" font-family="{MONO}" font-size="11" fill="{LINE_SOFT}" text-anchor="middle">{"ABCDEF"[j]}</text>')
            if 0 < j:
                for (xa, xb) in ((MARGIN, x0), (x1, W - MARGIN)):
                    out.append(f'<line x1="{xa}" y1="{y0 + zh * j}" x2="{xb}" y2="{y0 + zh * j}" stroke="{LINE_SOFT}" stroke-width="0.8"/>')
        # classification band
        for yy in (MARGIN - 8, H - MARGIN + 18):
            out.append(f'<text x="{W / 2}" y="{yy}" font-family="{MONO}" font-size="11" fill="{ACCENT}" text-anchor="middle" letter-spacing="3">{esc(BAND)}</text>')
        out.append(f'<text x="{MARGIN}" y="{MARGIN - 8}" font-family="{MONO}" font-size="11" fill="{LINE_SOFT}" letter-spacing="2">{esc(PROGRAMME)}</text>')
        out.append(f'<text x="{W - MARGIN}" y="{MARGIN - 8}" font-family="{MONO}" font-size="11" fill="{LINE_SOFT}" text-anchor="end" letter-spacing="2">{esc(self.number)}  REV {esc(self.rev)}</text>')
        return "\n".join(out)

    def _title_block(self) -> str:
        s = Sheet.__new__(Sheet)
        s.body = []
        x1, y1 = INNER[2], INNER[3]
        w, h = 520, 118
        x, y = x1 - w, y1 - h
        s.rect(x, y, w, h, sw=2.0, fill=GROUND_DK)
        # rows
        s.line(x, y + 30, x + w, y + 30, sw=1.0)
        s.line(x, y + 78, x + w, y + 78, sw=1.0)
        s.line(x + 300, y, x + 300, y + 30, sw=1.0)
        s.text(x + 8, y + 12, "PROGRAMME", size=8, color=LINE_SOFT, mono=True)
        s.text(x + 8, y + 25, PROGRAMME, size=12, weight="bold", mono=True)
        s.text(x + 308, y + 12, "DRAWING NO.", size=8, color=LINE_SOFT, mono=True)
        s.text(x + 308, y + 25, self.number, size=14, weight="bold", mono=True, color=ACCENT)
        s.text(x + 8, y + 42, "TITLE", size=8, color=LINE_SOFT, mono=True)
        s.text(x + 8, y + 58, self.title.upper(), size=13, weight="bold")
        if self.subtitle:
            sub = self.subtitle if len(self.subtitle) <= 92 else self.subtitle[:89].rstrip() + "…"
            s.text(x + 8, y + 72, sub, size=10, color=LINE_SOFT)
        cols = [("DRAWN", DRAWN, 110), ("CHECKED", CHECKED, 170), ("APPROVED", APPROVED, 70), ("DATE", DATE, 80), ("SCALE", self.scale, 50), ("SHEET", f"{self.sheet_no} OF {self.sheet_of}", 40)]
        cx = x
        for label, val, cw in cols:
            s.text(cx + 6, y + 90, label, size=8, color=LINE_SOFT, mono=True)
            s.text(cx + 6, y + 108, val, size=10, mono=True)
            cx += cw
            s.line(cx, y + 78, cx, y + h, sw=0.8)
        return "\n".join(s.body)

    def _rev_block(self) -> str:
        s = Sheet.__new__(Sheet)
        s.body = []
        x1, y0 = INNER[2], INNER[1]
        w = 420
        rows = self.revisions
        h = 20 + 18 * (len(rows) + 1)
        x = x1 - w
        s.rect(x, y0, w, h, sw=1.6, fill=GROUND_DK)
        s.text(x + 8, y0 + 14, "REVISIONS", size=9, color=LINE_SOFT, mono=True, spacing=2)
        s.line(x, y0 + 20, x + w, y0 + 20, sw=0.8)
        s.text(x + 8, y0 + 33, "REV", size=9, mono=True, color=ACCENT)
        s.text(x + 50, y0 + 33, "DESCRIPTION", size=9, mono=True, color=ACCENT)
        s.text(x + 330, y0 + 33, "DATE", size=9, mono=True, color=ACCENT)
        for i, (r, d, dt) in enumerate(rows):
            yy = y0 + 51 + 18 * i
            s.text(x + 8, yy, r, size=9, mono=True)
            s.text(x + 50, yy, d, size=9, mono=True)
            s.text(x + 330, yy, dt, size=9, mono=True)
        s.line(x + 44, y0 + 20, x + 44, y0 + h, sw=0.8)
        s.line(x + 324, y0 + 20, x + 324, y0 + h, sw=0.8)
        return "\n".join(s.body)

    def _notes_block(self) -> str:
        if not self.notes:
            return ""
        s = Sheet.__new__(Sheet)
        s.body = []
        x0, y0 = INNER[0], INNER[1]
        w = self.notes_width
        wrapped = []
        for i, n in enumerate(self.notes, 1):
            ls = textwrap.wrap(n, int(w / 6.9))
            wrapped.append(f"{i}. {ls[0]}")
            wrapped.extend("   " + l for l in ls[1:])
        h = 24 + 14 * len(wrapped) + 8
        s.rect(x0, y0, w, h, sw=1.4, fill=GROUND_DK, opacity=0.95)
        s.text(x0 + 8, y0 + 14, "GENERAL NOTES", size=9, color=LINE_SOFT, mono=True, spacing=2)
        s.line(x0, y0 + 20, x0 + w, y0 + 20, sw=0.8)
        s.lines(x0 + 8, y0 + 34, wrapped, size=10, lh=14, mono=True)
        return "\n".join(s.body)

    def _parts_block(self) -> str:
        if not self.parts:
            return ""
        s = Sheet.__new__(Sheet)
        s.body = []
        x0, y1 = INNER[0], INNER[3]
        w = self.parts_width
        lh = 18
        h = 24 + lh * (len(self.parts) + 1) + 6
        x, y = self.parts_pos if self.parts_pos != (0, 0) else (x0, y1 - h)
        s.rect(x, y, w, h, sw=1.6, fill=GROUND_DK, opacity=0.96)
        s.text(x + 8, y + 14, self.parts_title, size=9, color=LINE_SOFT, mono=True, spacing=2)
        s.line(x, y + 20, x + w, y + 20, sw=0.8)
        s.text(x + 8, y + 36, "NO", size=9, mono=True, color=ACCENT)
        s.text(x + 44, y + 36, "PART / FUNCTION", size=9, mono=True, color=ACCENT)
        s.text(x + 250, y + 36, "SPECIFICATION / WHERE USED", size=9, mono=True, color=ACCENT)
        for i, (n, name, spec) in enumerate(self.parts):
            yy = y + 36 + lh * (i + 1)
            s.text(x + 8, yy, str(n), size=10, mono=True, color=ACCENT)
            s.text(x + 44, yy, name, size=10, mono=True)
            s.text(x + 250, yy, spec, size=9, mono=True, color=LINE_SOFT)
        s.line(x + 38, y + 20, x + 38, y + h, sw=0.8)
        s.line(x + 244, y + 20, x + 244, y + h, sw=0.8)
        return "\n".join(s.body)

    def _refs_block(self) -> str:
        if not self.refs:
            return ""
        s = Sheet.__new__(Sheet)
        s.body = []
        x1, y1 = INNER[2], INNER[3]
        w, lh = 520, 13
        h = 22 + lh * len(self.refs)
        x, y = x1 - w, y1 - 118 - h - 6
        s.rect(x, y, w, h, sw=1.0, fill=GROUND_DK, opacity=0.95)
        s.text(x + 8, y + 13, "REFERENCE DOCUMENTS / SOURCE OF TRUTH", size=8, color=LINE_SOFT, mono=True, spacing=1)
        s.lines(x + 8, y + 28, self.refs, size=9, lh=lh, mono=True, color=LINE_SOFT)
        return "\n".join(s.body)

    def render(self) -> str:
        return "\n".join([self._frame(), *self.body, self._notes_block(), self._rev_block(), self._parts_block(),
                          self._refs_block(), self._title_block(), "</svg>"])


def zone(col: int, row: str) -> Tuple[float, float]:
    """centre of a zone, e.g. zone(4,'C'); columns count 8..1 left to right as printed."""
    x0, y0, x1, y1 = INNER
    zw = (x1 - x0) / 8
    zh = (y1 - y0) / 6
    i = 8 - col
    j = "ABCDEF".index(row)
    return x0 + zw * (i + 0.5), y0 + zh * (j + 0.5)
