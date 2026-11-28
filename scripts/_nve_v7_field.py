#!/usr/bin/env python3
"""v7 stage V2: a c0 FIELD for the segment certifier, built on the V1-validated evaluator (_nve_v7_c0.C0).

A Field holds, for one point k, the states (c0, c0', d c0/dk, d c0'/dk, sqrt B) at every point it has visited. It
answers the certifier's two kinds of query, replacing the Laurent evaluator (v2's laurent / c0_at):
  - at(z), z an exact point: continue C0 from the nearest cached state along a straight segment, or route from the
    base point z_s = R0 along the arc |z| = R0 and then radially;
  - box(Z): the state at Z's midpoint plus a Taylor remainder with M = sup |c0''| (and sup |d c0''/dk|) on a square
    containing Z, certified free of singularities by C0.sup_box.
Single-valuedness: every path stays in |z| > rho_safe = (largest modulus of c0's singular points at this k) + 0.05,
where c0 is single-valued (all periods vanish, as shown in CLOSURE_STOPC_RESULT.md). A query that would need a path
inside it is REFUSED with a RuntimeError, which v2's safe_step treats as a refused box (the caller halves rho).
"""
import cmath
import math

from flint import acb, arb

import _nve_v7_c0 as V7

GRID = 0.05


class Field:
    def __init__(self, spin, k, R0):
        self.c = V7.C0(spin, k if isinstance(k, acb) else acb(k), deriv=True)
        self.R0 = arb(R0) if not isinstance(R0, arb) else R0
        self.rho_safe = max(abs(p) for p in self.c.sing_points()) + 0.05
        if not float(self.R0.mid()) > self.rho_safe:
            raise RuntimeError(f"field: base circle R0 = {self.R0} not outside rho_safe = {self.rho_safe}")
        st = self.c.start(self.R0)
        self.cells = {}
        self._put(st)

    # ------------------------------------------------------------------------------------------ cache
    @staticmethod
    def _key(zc):
        return (math.floor(zc.real / GRID), math.floor(zc.imag / GRID))

    def _put(self, st):
        zc = complex(st["z"].mid())
        self.cells.setdefault(self._key(zc), []).append((zc, st))

    def _nearest(self, zc):
        i, j = self._key(zc)
        best, bd = None, None
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for zz, st in self.cells.get((i + di, j + dj), ()):
                    d = abs(zz - zc)
                    if bd is None or d < bd:
                        best, bd = st, d
        return best, bd

    def _seg_ok(self, z0, z1):
        """the straight segment z0 -> z1 stays in |z| > rho_safe"""
        d = z1 - z0
        if abs(d) == 0:
            return abs(z0) > self.rho_safe
        t = max(0.0, min(1.0, -(z0.real * d.real + z0.imag * d.imag) / (abs(d) ** 2)))
        return abs(z0 + t * d) > self.rho_safe

    # ------------------------------------------------------------------------------------------ queries
    def at(self, z):
        """the state at the exact point z (acb with zero radius)."""
        zc = complex(z.mid())
        if abs(zc) <= self.rho_safe:
            raise RuntimeError(f"field: query {zc} inside rho_safe = {self.rho_safe:.4f}")
        st, d = self._nearest(zc)
        if st is not None and d == 0 and z.real.rad() == 0 and z.imag.rad() == 0 and st["z"] == z:
            return st
        try:
            if st is not None and d < 4 * GRID and self._seg_ok(complex(st["z"].mid()), zc):
                out = self.c.walk([st["z"], z], st)
            else:
                out = self._route(z, zc)
        except AssertionError as e:
            raise RuntimeError(f"field: {e}")
        for s in out[1:]:
            self._put(s)
        return out[-1]

    def _route(self, z, zc):
        """from the base point along the arc |z| = R0 to arg(z), then radially to z."""
        base, = self.cells[self._key(complex(self.R0.mid()))][:1]
        st = base[1]
        th = cmath.phase(zc)
        R0f = float(self.R0.mid())
        n = max(1, int(abs(th) / (math.pi / 12)) + 1)
        verts = [st["z"]] + [acb(self.R0) * acb(0, arb(th) * j / n).exp() for j in range(1, n + 1)]
        if abs(abs(zc) - R0f) > 0:
            verts.append(z)
        if not all(self._seg_ok(complex(a.mid()), complex(b.mid())) for a, b in zip(verts[:-1], verts[1:])):
            raise RuntimeError(f"field: no safe route to {zc}")
        return self.c.walk(verts, st)

    def box(self, Z):
        """(c0, c0', D0, D1) enclosed on the box Z."""
        zm = acb(Z.real.mid(), Z.imag.mid())
        st = self.at(zm)
        r = max(Z.real.rad(), Z.imag.rad())
        if r == 0:
            return st["c0"], st["c0p"], st["D0"], st["D1"]
        r = arb(r).upper() * 1.0000001
        if not float(r) < abs(complex(zm.mid())) - self.rho_safe:
            raise RuntimeError("field: box reaches rho_safe")
        try:
            M, MD = self.c.sup_box(zm, r)
        except AssertionError as e:
            raise RuntimeError(f"field: {e}")
        dz = Z - zm
        d = (dz.abs_upper() * 1).upper()
        U = acb(arb(0, 1), arb(0, 1))
        c0p = st["c0p"] + (M * d).upper() * U
        c0 = st["c0"] + st["c0p"] * dz + (M * d * d / 2).upper() * U
        D1 = st["D1"] + (MD * d).upper() * U
        D0 = st["D0"] + st["D1"] * dz + (MD * d * d / 2).upper() * U
        return c0, c0p, D0, D1


class View:
    """what v2's laurent(k[, deriv]) returns under v7: c0_at(z, view) gives (c0, c0') or (D0, D1)."""
    def __init__(self, field, deriv):
        self.field, self.deriv = field, deriv

    def c0_at(self, z):
        if z.real.rad() == 0 and z.imag.rad() == 0:
            st = self.field.at(z)
            return (st["D0"], st["D1"]) if self.deriv else (st["c0"], st["c0p"])
        c0, c0p, D0, D1 = self.field.box(z)
        return (D0, D1) if self.deriv else (c0, c0p)
