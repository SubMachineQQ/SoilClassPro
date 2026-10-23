from __future__ import annotations

import textwrap
from typing import Iterable, List, Sequence, Tuple

from matplotlib.text import Annotation, Text
from matplotlib.transforms import Bbox

Candidate = Tuple[float, float, str, str]

AROUND_POINT: List[Candidate] = [
    (11, 9, "left", "bottom"), (-11, 9, "right", "bottom"),
    (11, -9, "left", "top"), (-11, -9, "right", "top"),
    (16, 32, "left", "bottom"), (-16, 32, "right", "bottom"),
    (16, -32, "left", "top"), (-16, -32, "right", "top"),
    (0, 44, "center", "bottom"), (0, -44, "center", "top"),
    (44, 0, "left", "center"), (-44, 0, "right", "center"),
    (40, 60, "left", "bottom"), (-40, 60, "right", "bottom"),
    (40, -60, "left", "top"), (-40, -60, "right", "top"),
    (80, 20, "left", "bottom"), (-80, 20, "right", "bottom"),
    (80, -20, "left", "top"), (-80, -20, "right", "top"),
]

SMALL_AROUND: List[Candidate] = [
    (4, 4, "left", "bottom"), (-4, 4, "right", "bottom"),
    (4, -4, "left", "top"), (-4, -4, "right", "top"),
    (0, 7, "center", "bottom"), (0, -7, "center", "top"),
    (7, 0, "left", "center"), (-7, 0, "right", "center"),
    (9, 9, "left", "bottom"), (-9, 9, "right", "bottom"),
    (9, -9, "left", "top"), (-9, -9, "right", "top"),
]

NUDGE: List[Candidate] = [(0, 0, "center", "center")] + [
    (dx, dy, "center", "center")
    for dy, dx in ((7, 0), (-7, 0), (0, 12), (0, -12), (13, 0), (-13, 0),
                   (7, 12), (7, -12), (-7, 12), (-7, -12), (19, 0), (-19, 0),
                   (0, 22), (0, -22), (25, 0), (-25, 0))
]


def ring(distances: Sequence[float]) -> List[Candidate]:
    out: List[Candidate] = []
    for d in distances:
        out += [(d, d, "left", "bottom"), (-d, d, "right", "bottom"),
                (d, -d, "left", "top"), (-d, -d, "right", "top"),
                (0, d * 1.4, "center", "bottom"), (0, -d * 1.4, "center", "top"),
                (d * 1.4, 0, "left", "center"), (-d * 1.4, 0, "right", "center")]
    return out


FAR_AROUND: List[Candidate] = AROUND_POINT + [
    (dx, dy, "center", "bottom" if dy > 0 else "top")
    for dy in (50, 70, 90, 110, 130, 150, 170, 190, 220, -60, -90, -120)
    for dx in (0, -30, 30, -60, 60, -90, 90, -120, 120, -160, 160, -200, 200,
               -240, 240)
] + [
    (dx, dy, "left" if dx > 0 else "right", "center")
    for dx in (120, -120, 150, -150, 190, -190, 230, -230, 270, -270)
    for dy in (0, 30, 60, 90, 120, 150, 180, -30, -60)
]


def wrap_label(text: str, width: int = 26) -> str:
    lines = []
    for line in str(text).split("\n"):
        lines.extend(textwrap.wrap(line, width=width, break_long_words=True)
                     or [""])
    return "\n".join(lines)


def movable(text: Text, candidates: Sequence[Candidate], priority: int = 0,
            region: str = "axes") -> Text:
    text._soil_candidates = list(candidates)
    text._soil_priority = priority
    text._soil_region = region
    if not isinstance(text, Annotation):
        text._soil_base = text.get_position()
    return text


def keep_clear(ax, x: float, y: float, radius_pt: float = 9.0) -> None:
    points = getattr(ax, "_soil_points", None)
    if points is None:
        points = ax._soil_points = []
    points.append((x, y, radius_pt))


def _tick_labels(axis, low, high) -> Iterable[Text]:
    lo, hi = sorted((low, high))
    span = (hi - lo) * 1e-6
    for tick in axis.get_major_ticks():
        loc = tick.get_loc()
        if loc is None or not lo - span <= loc <= hi + span:
            continue
        for label in (tick.label1, tick.label2):
            if label.get_visible():
                yield label


def _texts(fig) -> Iterable[Text]:
    yield from fig.texts
    for ax in fig.axes:
        yield from ax.texts
        if ax.axison:
            if ax.xaxis.get_visible():
                yield from _tick_labels(ax.xaxis, *ax.get_xlim())
                yield ax.xaxis.label
            if ax.yaxis.get_visible():
                yield from _tick_labels(ax.yaxis, *ax.get_ylim())
                yield ax.yaxis.label
        yield ax.title


def _extent(text: Text, renderer) -> Bbox:
    if isinstance(text, Annotation):
        text.update_positions(renderer)
        box = Text.get_window_extent(text, renderer)
    else:
        box = text.get_window_extent(renderer)
    factor = 0.45 if text.get_bbox_patch() is not None else 0.18
    pad = factor * text.get_fontsize() * renderer.points_to_pixels(1.0)
    return Bbox.from_extents(box.x0 - pad, box.y0 - pad, box.x1 + pad,
                             box.y1 + pad)


def _area(a: Bbox, b: Bbox) -> float:
    w = min(a.x1, b.x1) - max(a.x0, b.x0)
    h = min(a.y1, b.y1) - max(a.y0, b.y0)
    return w * h if w > 0 and h > 0 else 0.0


def _outside(box: Bbox, region: Bbox) -> float:
    dx = max(0.0, region.x0 - box.x0) + max(0.0, box.x1 - region.x1)
    dy = max(0.0, region.y0 - box.y0) + max(0.0, box.y1 - region.y1)
    return (dx + dy) * max(box.width, box.height)


def _apply(text: Text, candidate: Candidate, renderer) -> None:
    dx, dy, ha, va = candidate
    text.set_horizontalalignment(ha)
    text.set_verticalalignment(va)
    if isinstance(text, Annotation):
        text.xyann = (dx, dy)
        return
    ax = text.axes
    base = ax.transData.transform(text._soil_base)
    scale = renderer.points_to_pixels(1.0)
    moved = (base[0] + dx * scale, base[1] + dy * scale)
    text.set_position(ax.transData.inverted().transform(moved))


def _leader_hits(text: Text, box: Bbox, obstacles, renderer) -> float:
    if (not isinstance(text, Annotation) or text.arrow_patch is None
            or text.xycoords != "data" or text.axes is None):
        return 0.0
    x0, y0 = text.axes.transData.transform(text.xy)
    x1 = min(max(x0, box.x0), box.x1)
    y1 = min(max(y0, box.y0), box.y1)
    length = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    if length < 4.0:
        return 0.0
    near = renderer.points_to_pixels(10.0)
    hits = 0.0
    steps = max(8, int(length / 3.0))
    for i in range(1, steps):
        f = i / steps
        px, py = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        if ((px - x0) ** 2 + (py - y0) ** 2) ** 0.5 < near:
            continue
        if any(o.x0 <= px <= o.x1 and o.y0 <= py <= o.y1 for o in obstacles):
            hits += 40.0
    return hits


def declutter(fig, renderer=None) -> None:
    if renderer is None:
        renderer = fig.canvas.get_renderer()
    for ax in fig.axes:
        ax.apply_aspect()
    texts =[t for t in _texts(fig) if t.get_visible() and t.get_text()]
    movers = sorted((t for t in texts if hasattr(t, "_soil_candidates")),
                    key=lambda t: t._soil_priority)
    if not movers:
        return
    obstacles = [_extent(t, renderer) for t in texts
                 if not hasattr(t, "_soil_candidates")]
    for ax in fig.axes:
        legend = ax.get_legend()
        if legend is not None:
            obstacles.append(legend.get_window_extent(renderer))
        scale = renderer.points_to_pixels(1.0)
        for x, y, radius in getattr(ax, "_soil_points", []):
            px, py = ax.transData.transform((x, y))
            r = radius * scale
            obstacles.append(Bbox.from_extents(px - r, py - r, px + r, py + r))
    for text in movers:
        ax = text.axes
        region = (ax.get_window_extent(renderer)
                  if text._soil_region == "axes" and ax is not None
                  else fig.bbox)
        best, best_score = None, None
        for candidate in text._soil_candidates:
            _apply(text, candidate, renderer)
            box = _extent(text, renderer)
            score = (sum(_area(box, other) for other in obstacles)
                     + _outside(box, region)
                     + _leader_hits(text, box, obstacles, renderer))
            if best_score is None or score < best_score:
                best, best_score = candidate, score
            if score == 0:
                break
        _apply(text, best, renderer)
        obstacles.append(_extent(text, renderer))
