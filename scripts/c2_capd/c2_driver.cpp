// C2 driver (C2_REGISTRATION.md, addendum C2-1): CAPD's MPFR C0 doubleton solver encloses the monodromy of the
// rho-equation along closed polygon loops, over a complex k-sub-box, with the k-correlation kept as C*r0.
//
// The system (complex, written as 16 real states), on the edge z = P_j + (t - j) h_j, t in [j, j+1]:
//   s   = sqrt B carried as a state:  ds/dz   = B_z / (2 s),   B = c2 w^2 + c1 w + cc,  w = z^2/a^2,
//                                      c2 = 90 - 21k, c1 = -(60 - 18k), cc = 10 - k
//   c0:                                dc0/dz  = c0',   dc0'/dz = pref * s / (z^2 + a^2)^3,   pref = -sqrt(8/5) a^3
//   Y (2x2, rows (y, y')):             dY/dz   = [[0, 1], [-q, 0]] Y,   q = (3/16) lam^2,
//                                      lam = G1'/G1 - G2'/G2,  G2 = f0^2 + c0^2,  G1 = E2 G2 - f0,
//                                      f0 = (z^2 - 2z + a^2)/(z^2 + a^2),  f0' = 2(z^2 - a^2)/(z^2 + a^2)^2
//   k:                                 dk/dz   = 0
// Every right-hand side is rational in (z, k, s, c0, c0', Y); d/dt = h d/dz.
// State order: 0,1 s | 2,3 c0 | 4,5 c0' | 6,7 Y00 | 8,9 Y01 | 10,11 Y10 | 12,13 Y11 | 14,15 k   (re, im pairs).
//
// Rules (Quantum's, mandatory in addendum C2-1):
//  * MPFR intervals only: a compile-time guard rejects every other scalar type (native double intervals, DMap,
//    LDMap / long double, MpMap / non-interval MPFR). c2_guard_check.sh shows each plant failing to compile.
//  * After EVERY step: every enclosure finite, and |s| > 0, z^2 + a^2 != 0, G1 != 0, G2 != 0 certified on the
//    WHOLE-STEP enclosure (getLastEnclosure, with z over the step's whole time interval). Any failure REFUSES:
//    the output says REFUSED and the exit code is 2. Exceptions from CAPD also refuse.
//  * Step sizes logged (one line per step).
//
// Usage: c2_driver <input> <output> <steplog>
// Input and output numbers are EXACT binary values written "mantissa exponent" (value = mantissa * 2^exponent),
// so nothing is rounded crossing the Python/C++ boundary (input exactness is asserted).
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <type_traits>
#include <vector>

#include <gmp.h>
#include <mpfr.h>

#include "capd/capdlib.h"
#include "capd/mpcapdlib.h"
#include "capd/dynset/C0DoubletonSet.hpp"   // instantiates the no-reorganization doubleton below

using capd::autodiff::Node;

// ------------------------------------------------------------------------------------------------ the guard
#if defined(C2_PLANT_IMAP)
typedef capd::IMap MapT;          // native double intervals
#elif defined(C2_PLANT_DMAP)
typedef capd::DMap MapT;          // double, non-interval
#elif defined(C2_PLANT_LDMAP)
typedef capd::LDMap MapT;         // long double, non-interval
#elif defined(C2_PLANT_MPMAP)
typedef capd::MpMap MapT;         // MPFR, non-interval
#else
typedef capd::MpIMap MapT;        // MPFR intervals: the only admissible type
#endif
typedef capd::dynsys::OdeSolver<MapT> SolverT;
typedef capd::poincare::TimeMap<SolverT> TimeMapT;
typedef MapT::ScalarType IT;
typedef MapT::MatrixType MatT;
typedef MapT::VectorType VecT;
static_assert(std::is_same<IT, capd::MpInterval>::value,
              "C2 GUARD: proof code admits MPFR intervals (capd::MpInterval) only");
static_assert(std::is_same<SolverT::ScalarType, capd::MpInterval>::value,
              "C2 GUARD: the solver must run on MPFR intervals only");
static_assert(std::is_same<MatT, capd::MpIMatrix>::value, "C2 GUARD: MPFR interval matrices only");
// The doubleton set x + C r0 + B r, WITHOUT reorganization, so the k-dependence stays in C r0 (r0 = the dk box).
// The QR policy for B (no reorganization in any case): C2_POLICY_ID keeps r coordinate-aligned (B = I), which respects
// the system's block-triangular structure ((s, c0, c0', k) never see Y); the default is CAPD's Rect2 QR with pivoting.
#if defined(C2_POLICY_ID)
typedef capd::dynset::C0DoubletonSet<MatT, capd::dynset::DefaultPolicy> SetT;
static const char* POLICY = "IdQR (B = I)";
#elif defined(C2_POLICY_INVQR)
typedef capd::dynset::C0DoubletonSet<MatT, capd::dynset::InverseQRPolicy<>> SetT;
static const char* POLICY = "InverseQR";
#else
typedef capd::dynset::C0DoubletonSet<MatT, capd::dynset::FullQRWithPivoting<>> SetT;
static const char* POLICY = "FullQRWithPivoting";
#endif

static const int DIM = 16, NPAR = 8;
static long PREC = 256;

static void die(const std::string& m) {
  std::cerr << "c2_driver: " << m << std::endl;
  std::exit(3);
}

// ------------------------------------------------------------------------------------------------ exact I/O
struct MpAcc : capd::MpFloat {
  static mpfr_srcptr get(const capd::MpFloat& r) { return (r.*(&MpAcc::mpfr_rep)); }
  static mpfr_ptr mut(capd::MpFloat& r) { return (r.*(&MpAcc::mpfr_rep)); }
};

static capd::MpFloat readF(std::istream& in) {
  std::string m;
  long e;
  if (!(in >> m >> e)) die("input: expected 'mantissa exponent'");
  mpz_t z;
  if (mpz_init_set_str(z, m.c_str(), 10) != 0) die("input: bad mantissa " + m);
  mpfr_t t;
  mpfr_init2(t, PREC);
  if (mpfr_set_z(t, z, MPFR_RNDN) != 0) die("input: mantissa not exact at this precision: " + m);
  if (mpfr_mul_2si(t, t, e, MPFR_RNDN) != 0) die("input: exponent overflow");
  capd::MpFloat f;                                   // default precision = PREC (set before any read)
  if (mpfr_get_prec(MpAcc::get(f)) != PREC) die("input: MpFloat precision differs from PREC");
  mpfr_set(MpAcc::mut(f), t, MPFR_RNDN);
  if (mpfr_cmp(MpAcc::get(f), t) != 0) die("input: conversion not exact");
  mpz_clear(z);
  mpfr_clear(t);
  return f;
}

static IT readPoint(std::istream& in) {
  capd::MpFloat f = readF(in);
  return IT(f, f);
}

static IT readInterval(std::istream& in) {
  capd::MpFloat lo = readF(in), hi = readF(in);
  if (lo > hi) die("input: interval with lo > hi");
  return IT(lo, hi);
}

static std::string ex(const capd::MpFloat& f) {
  mpfr_srcptr p = MpAcc::get(f);
  if (!mpfr_number_p(p)) return "nan 0";
  if (mpfr_zero_p(p)) return "0 0";
  mpz_t m;
  mpz_init(m);
  mpfr_exp_t e = mpfr_get_z_2exp(m, p);
  char* s = mpz_get_str(nullptr, 10, m);
  std::string out = std::string(s) + " " + std::to_string((long)e);
  std::free(s);
  mpz_clear(m);
  return out;
}

static double dbl(const capd::MpFloat& f) { return mpfr_get_d(MpAcc::get(f), MPFR_RNDN); }   // for the log only

static std::string exI(const IT& x) { return ex(x.leftBound()) + " " + ex(x.rightBound()); }

static bool finiteI(const IT& x) {
  return mpfr_number_p(MpAcc::get(x.leftBound())) && mpfr_number_p(MpAcc::get(x.rightBound()));
}

// ------------------------------------------------------------------------------------------------ complex helpers
template <class T> struct Cx { T re, im; };
template <class T> Cx<T> operator+(const Cx<T>& a, const Cx<T>& b) { return {a.re + b.re, a.im + b.im}; }
template <class T> Cx<T> operator-(const Cx<T>& a, const Cx<T>& b) { return {a.re - b.re, a.im - b.im}; }
template <class T> Cx<T> operator*(const Cx<T>& a, const Cx<T>& b) {
  return {a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re};
}
template <class T> Cx<T> scale(const Cx<T>& a, const T& c) { return {a.re * c, a.im * c}; }
template <class T> Cx<T> operator/(const Cx<T>& a, const Cx<T>& b) {
  T n = b.re * b.re + b.im * b.im;
  return {(a.re * b.re + a.im * b.im) / n, (a.im * b.re - a.re * b.im) / n};
}
template <class T> T abs2(const Cx<T>& a) { return a.re * a.re + a.im * a.im; }

// The constants enter as T: Node(v) registers an exact double constant in the DAG; IT(v) is the exact interval.
template <class T> struct Q {
  Cx<T> D, f0, f0p, G1, G2, dG1, dG2;
};
template <class T> Q<T> quants(const Cx<T>& z, const Cx<T>& c0, const Cx<T>& c0p, const T& a, const T& E2,
                               const T& two, const T& zero) {
  Q<T> r;
  T a2 = a * a;
  Cx<T> z2 = z * z;
  Cx<T> A2 = {a2, zero};
  r.D = z2 + A2;
  r.f0 = (z2 - scale(z, two) + A2) / r.D;
  r.f0p = scale(z2 - A2, two) / (r.D * r.D);
  r.G2 = r.f0 * r.f0 + c0 * c0;
  r.dG2 = scale(r.f0 * r.f0p + c0 * c0p, two);
  r.G1 = scale(r.G2, E2) - r.f0;
  r.dG1 = scale(r.dG2, E2) - r.f0p;
  return r;
}

// ------------------------------------------------------------------------------------------------ the vector field
// params: 0 a | 1 E2 | 2 pref | 3 Re P_j | 4 Im P_j | 5 Re h_j | 6 Im h_j | 7 t_j (= j)
void field(Node t, Node in[], int, Node out[], int, Node par[], int) {
  Node two(2.0), zero(0.0);
  Node a = par[0], E2 = par[1], pref = par[2];
  Cx<Node> h = {par[5], par[6]};
  Cx<Node> z = {par[3] + (t - par[7]) * par[5], par[4] + (t - par[7]) * par[6]};
  Cx<Node> s = {in[0], in[1]}, c0 = {in[2], in[3]}, c0p = {in[4], in[5]};
  Cx<Node> y00 = {in[6], in[7]}, y01 = {in[8], in[9]}, y10 = {in[10], in[11]}, y11 = {in[12], in[13]};
  Cx<Node> k = {in[14], in[15]};
  Node a2 = a * a;
  Cx<Node> z2 = z * z;
  Cx<Node> w = {z2.re / a2, z2.im / a2};
  Cx<Node> c2 = {90.0 - 21.0 * k.re, -21.0 * k.im};
  Cx<Node> c1 = {-60.0 + 18.0 * k.re, 18.0 * k.im};
  Cx<Node> Bz = scale(z, two / a2) * (scale(c2 * w, two) + c1);
  Cx<Node> ds = Bz / scale(s, two);
  Q<Node> qq = quants(z, c0, c0p, a, E2, two, zero);
  Cx<Node> D3 = qq.D * qq.D * qq.D;
  Cx<Node> dc0p = scale(s, pref) / D3;
  Cx<Node> lam = qq.dG1 / qq.G1 - qq.dG2 / qq.G2;
  Cx<Node> q = scale(lam * lam, Node(0.1875));
  Cx<Node> mq = {-q.re, -q.im};
  Cx<Node> d[7] = {ds, c0p, dc0p, y10, y11, mq * y00, mq * y01};
  for (int i = 0; i < 7; ++i) {
    Cx<Node> o = h * d[i];
    out[2 * i] = o.re;
    out[2 * i + 1] = o.im;
  }
  out[14] = in[14] * 0.0;
  out[15] = in[15] * 0.0;
}

// ------------------------------------------------------------------------------------------------ main
int main(int argc, char** argv) {
  if (argc != 4) die("usage: c2_driver <input> <output> <steplog>");
  std::ifstream in(argv[1]);
  if (!in) die("cannot open input");
  std::string tag;
  in >> tag >> PREC;
  if (tag != "prec") die("input: expected prec");
  capd::MpFloat::setDefaultPrecision(PREC);
  int order;
  in >> tag >> order;
  if (tag != "order") die("input: expected order");
  in >> tag;
  if (tag != "tol") die("input: expected tol");
  double tol;                      // step-control tolerance (a double in CAPD's step control; it steers the step size
  in >> tol;                       // only and plays no part in the enclosure)
  in >> tag;
  if (tag != "a") die("input: expected a");
  IT a = readInterval(in);
  in >> tag;
  if (tag != "E2") die("input: expected E2");
  IT E2 = readInterval(in);
  in >> tag;
  if (tag != "pref") die("input: expected pref");
  IT pref = readInterval(in);
  in >> tag;
  if (tag != "R") die("input: expected R");
  capd::MpFloat R = readF(in);
  VecT x(DIM), r0(DIM), rv(DIM);
  MatT C(DIM, DIM);
  in >> tag;
  if (tag != "x") die("input: expected x");
  for (int i = 0; i < DIM; ++i) x[i] = readPoint(in);
  in >> tag;
  if (tag != "C") die("input: expected C");
  for (int i = 0; i < DIM; ++i) {
    for (int j = 0; j < DIM; ++j) C[i][j] = IT(0);
    C[i][14] = readPoint(in);
    C[i][15] = readPoint(in);
  }
  in >> tag;
  if (tag != "r") die("input: expected r");
  for (int i = 0; i < DIM; ++i) {
    capd::MpFloat ri = readF(in);
    if (ri < 0) die("input: negative radius");
    rv[i] = IT(-ri, ri);
    r0[i] = IT(0);
  }
  r0[14] = IT(-R, R);
  r0[15] = IT(-R, R);
  int nloops;
  in >> tag >> nloops;
  if (tag != "nloops") die("input: expected nloops");
  std::vector<std::vector<std::pair<IT, IT>>> loops(nloops);
  for (int l = 0; l < nloops; ++l) {
    int n;
    in >> tag >> n;
    if (tag != "loop") die("input: expected loop");
    for (int v = 0; v < n; ++v) {
      IT re = readPoint(in), im = readPoint(in);
      loops[l].push_back({re, im});
    }
    if (!(loops[l].front().first == loops[l].back().first) || !(loops[l].front().second == loops[l].back().second))
      die("input: loop not closed");
  }

  std::ofstream out(argv[2]), slog(argv[3]);
  out << "c2_driver prec " << PREC << " order " << order << " dim " << DIM << " policy " << POLICY << "\n";
  slog << "loop edge step t dt min|s|^2 min|D|^2 min|G1|^2 min|G2|^2 maxdiam\n";
  IT two(2), zero(0);

  MapT vf(field, DIM, DIM, NPAR);
  vf.setParameter(0, a);
  vf.setParameter(1, E2);
  vf.setParameter(2, pref);
  SolverT solver(vf, order);
  solver.setAbsoluteTolerance(tol);
  solver.setRelativeTolerance(tol);
  TimeMapT timeMap(solver);

  for (int l = 0; l < nloops; ++l) {
    SetT set(x, C, r0, rv, IT(0));
    long nsteps = 0;
    double dtmin = 1e300, dtmax = 0;
    const auto& P = loops[l];
    for (size_t j = 0; j + 1 < P.size(); ++j) {
      IT hre = P[j + 1].first - P[j].first, him = P[j + 1].second - P[j].second;
      IT tj((double)j);
      solver.getVectorField().setParameter(3, P[j].first);
      solver.getVectorField().setParameter(4, P[j].second);
      solver.getVectorField().setParameter(5, hre);
      solver.getVectorField().setParameter(6, him);
      solver.getVectorField().setParameter(7, tj);
      IT tfinal((double)(j + 1));
      timeMap.stopAfterStep(true);
      IT tprev = set.getCurrentTime();
      do {
        try {
          timeMap(tfinal, set);
        } catch (std::exception& e) {
          out << "REFUSED loop " << l << " edge " << j << " step " << nsteps << " capd exception: " << e.what() << "\n";
          slog << "REFUSED capd exception: " << e.what() << "\n";
          return 2;
        }
        IT tcur = set.getCurrentTime();
        ++nsteps;
        const VecT& E = set.getLastEnclosure();
        VecT hull = (VecT)set;
        bool fin = true;
        for (int i = 0; i < DIM; ++i) fin = fin && finiteI(E[i]) && finiteI(hull[i]);
        IT T = IT(tprev.leftBound(), tcur.rightBound()) - tj;
        Cx<IT> z = {P[j].first + T * hre, P[j].second + T * him};
        Cx<IT> s = {E[0], E[1]}, c0 = {E[2], E[3]}, c0p = {E[4], E[5]};
        Q<IT> qq = quants(z, c0, c0p, a, E2, two, zero);
        IT ms = abs2(s), mD = abs2(qq.D), m1 = abs2(qq.G1), m2 = abs2(qq.G2);
        bool dom = fin && finiteI(ms) && finiteI(mD) && finiteI(m1) && finiteI(m2) && ms.leftBound() > 0 &&
                   mD.leftBound() > 0 && m1.leftBound() > 0 && m2.leftBound() > 0;
        double dt = dbl(tcur.rightBound()) - dbl(tprev.leftBound());
        dtmin = std::min(dtmin, dt);
        dtmax = std::max(dtmax, dt);
        double md = 0;
        for (int i = 0; i < DIM; ++i) md = std::max(md, dbl(diam(hull[i]).rightBound()));
        slog << l << " " << j << " " << nsteps << " " << dbl(tcur.rightBound()) << " " << dt << " "
             << dbl(ms.leftBound()) << " " << dbl(mD.leftBound()) << " " << dbl(m1.leftBound()) << " "
             << dbl(m2.leftBound()) << " " << md << "\n";
        if (!dom) {
          out << "REFUSED loop " << l << " edge " << j << " step " << nsteps
              << (fin ? " domain not certified on the whole-step enclosure" : " non-finite enclosure") << "\n";
          slog << "REFUSED\n";
          return 2;
        }
        tprev = tcur;
      } while (!timeMap.completed());
      // the set's time is an interval a few ulps wide: it must contain the edge's final time and be negligibly wide
      // (the next edge's z-enclosure uses the whole time interval, so the slack is carried rigorously)
      IT tend = set.getCurrentTime();
      if (!(tend.leftBound() <= tfinal.leftBound() && tfinal.rightBound() <= tend.rightBound()) ||
          !(diam(tend).rightBound() < capd::MpFloat(1e-60))) {
        slog.flush();
        out << "REFUSED loop " << l << " edge " << j << " step " << nsteps << " the edge did not end at its final time: "
            << "set time [" << dbl(tend.leftBound()) << ", " << dbl(tend.rightBound())
            << "], final " << j + 1 << ", last step " << dbl(solver.getStep().leftBound()) << "\n";
        return 2;
      }
    }
    const VecT& sx = set.get_x();
    const MatT& sC = set.get_C();
    VecT Br = set.get_B() * set.get_r();
    VecT hull = (VecT)set;
    out << "loop " << l << " steps " << nsteps << " dtmin " << dtmin << " dtmax " << dtmax << "\n";
    for (int i = 0; i < DIM; ++i) {
      // C r0 with r0 zero off the k components: only columns 14, 15 enter; the other columns are checked to be
      // irrelevant by r0 being exactly zero there (asserted on the final set).
      if (!(set.get_r0()[i] == r0[i])) die("r0 changed during the integration");
      out << "row " << i << " x " << exI(sx[i]) << " c14 " << exI(sC[i][14]) << " c15 " << exI(sC[i][15]) << " br "
          << exI(Br[i]) << " hull " << exI(hull[i]) << "\n";
    }
  }
  out << "DONE\n";
  return 0;
}
