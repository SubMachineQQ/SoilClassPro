from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple


def _pchip_slopes(x: List[float], y: List[float]) -> List[float]:
    n = len(x)
    h = [x[i + 1] - x[i] for i in range(n - 1)]
    delta = [(y[i + 1] - y[i]) / h[i] for i in range(n - 1)]

    if n == 2:
        return [delta[0], delta[0]]

    m = [0.0] * n
    for i in range(1, n - 1):
        d0, d1 = delta[i - 1], delta[i]
        if d0 == 0.0 or d1 == 0.0 or (d0 > 0) != (d1 > 0):
            m[i] = 0.0
        else:
            w0, w1 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w0 + w1) / (w0 / d0 + w1 / d1)

    def edge(h0, h1, d0, d1):
        m_end = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1)
        if (m_end > 0) != (d0 > 0) and m_end != 0 and d0 != 0:
            return 0.0
        if (d0 > 0) != (d1 > 0) and abs(m_end) > abs(3 * d0):
            return 3 * d0
        return m_end

    m[0] = edge(h[0], h[1], delta[0], delta[1]) if n > 2 else delta[0]
    m[-1] = edge(h[-1], h[-2], delta[-1], delta[-2]) if n > 2 else delta[-1]
    return m


def _hermite(x0, x1, y0, y1, m0, m1, xq):
    h = x1 - x0
    t = (xq - x0) / h
    t2, t3 = t * t, t * t * t
    h00 = 2 * t3 - 3 * t2 + 1
    h10 = t3 - 2 * t2 + t
    h01 = -2 * t3 + 3 * t2
    h11 = t3 - t2
    return h00 * y0 + h10 * h * m0 + h01 * y1 + h11 * h * m1


def _hermite_deriv(x0, x1, y0, y1, m0, m1, xq):
    h = x1 - x0
    t = (xq - x0) / h
    dh00 = 6 * t * t - 6 * t
    dh10 = 3 * t * t - 4 * t + 1
    dh01 = -6 * t * t + 6 * t
    dh11 = 3 * t * t - 2 * t
    return (dh00 * y0 + dh10 * h * m0 + dh01 * y1 + dh11 * h * m1) / h


class GsdCurve:
    def __init__(self, sieve_data: Sequence[Tuple[float, float]]):
        sizes = [d for d, _ in sieve_data]
        passing = [p for _, p in sieve_data]
        xs = [math.log10(s) for s in sizes]

        x: List[float] = []
        y: List[float] = []
        for xi, yi in zip(xs, passing):
            if x and abs(xi - x[-1]) < 1e-12:
                y[-1] = (y[-1] + yi) / 2.0
            else:
                x.append(xi)
                y.append(float(yi))

        self._x = x
        self._y = y
        self._m = _pchip_slopes(x, y)
        self.x_min = x[0]
        self.x_max = x[-1]
        self.y_min = min(y)
        self.y_max = max(y)

    def _segment(self, lx: float) -> int:
        x = self._x
        if lx <= x[0]:
            return 0
        if lx >= x[-1]:
            return len(x) - 2
        lo, hi = 0, len(x) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if x[mid] <= lx:
                lo = mid
            else:
                hi = mid
        return lo

    def value_at(self, size_mm: float) -> float:
        lx = math.log10(size_mm)
        if lx <= self.x_min:
            return self._y[0]
        if lx >= self.x_max:
            return self._y[-1]
        i = self._segment(lx)
        return _hermite(self._x[i], self._x[i + 1], self._y[i], self._y[i + 1],
                        self._m[i], self._m[i + 1], lx)

    def slope_at_log_size(self, log_size: float) -> float:
        lx = min(max(log_size, self.x_min), self.x_max)
        i = self._segment(lx)
        return _hermite_deriv(self._x[i], self._x[i + 1], self._y[i],
                             self._y[i + 1], self._m[i], self._m[i + 1], lx)

    def size_at(self, percent: float) -> Optional[float]:
        if percent < self.y_min or percent > self.y_max:
            return None

        x = self._x
        for i in range(len(x) - 1):
            y0, y1 = self._y[i], self._y[i + 1]
            lo, hi = min(y0, y1), max(y0, y1)
            if lo - 1e-9 <= percent <= hi + 1e-9:
                if y0 == percent:
                    return 10 ** x[i]
                if y1 == percent:
                    return 10 ** x[i + 1]
                lo_x, hi_x = x[i], x[i + 1]
                f_lo = _hermite(x[i], x[i + 1], y0, y1, self._m[i],
                               self._m[i + 1], lo_x) - percent
                for _ in range(80):
                    mid = (lo_x + hi_x) / 2.0
                    f_mid = _hermite(x[i], x[i + 1], y0, y1, self._m[i],
                                    self._m[i + 1], mid) - percent
                    if abs(f_mid) < 1e-10:
                        return 10 ** mid
                    if (f_lo > 0) == (f_mid > 0):
                        lo_x, f_lo = mid, f_mid
                    else:
                        hi_x = mid
                return 10 ** ((lo_x + hi_x) / 2.0)
        return None
