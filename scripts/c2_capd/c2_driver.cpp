// C2 driver (C2_REGISTRATION.md, addendum C2-1): CAPD's MPFR C0 doubleton solver encloses the monodromy of the
// rho-equation along closed polygon loops, over a complex k-sub-box, with the k-correlation kept as C*r0.
//
// The system (complex, written as 16 real states), on the edge z = P_j + (t - j) h_j, t in [j, j+1]:
//   s = sqrt B is NOT a state (addendum C2-4): a closed-form PRINCIPAL root, B = c2 w^2 + c1 w + cc, w = z^2/a^2,
//       c2 = 90 - 21k, c1 = -(60 - 18k), cc = 10 - k;   sform disc: s = sqrt_p(B);  sform circle: s = w sqrt_p(I),
//       I = c2 + c1/w + cc/w^2;   sqrt_p(A) = (sqrt((|A| + Re A)/2), Im A / (2 sqrt((|A| + Re A)/2)))
//   c0:                                dc0/dz  = c0',   dc0'/dz = pref * s / (z^2 + a^2)^3,   pref = -sqrt(8/5) a^3
//   Y (2x2, rows (y, y')):             dY/dz   = [[0, 1], [-q, 0]] Y,   q = (3/16) lam^2,
//                                      lam = G1'/G1 - G2'/G2,  G2 = f0^2 + c0^2,  G1 = E2 G2 - f0,
//                                      f0 = (z^2 - 2z + a^2)/(z^2 + a^2),  f0' = 2(z^2 - a^2)/(z^2 + a^2)^2
//   k:                                 dk/dz   = 0
// Every right-hand side is rational in (z, k, s, c0, c0', Y); d/dt = h d/dz.
// State order: 0,1 c0 | 2,3 c0' | 4,5 Y00 | 6,7 Y01 | 8,9 Y10 | 10,11 Y11 | 12,13 k   (re, im pairs).
//
// Rules (Quantum's, mandatory in addendum C2-1):
//  * MPFR intervals only: a compile-time guard rejects every other scalar type (native double intervals, DMap,
//    LDMap / long double, MpMap / non-interval MPFR). c2_guard_check.sh shows each plant failing to compile.
//  * The root's branch (C2-4 (a1), (a2)): s depends only on (z, k), so BEFORE each edge the root's argument A is
//    certified off the cut (lower(|A| + Re A) > 0) and, on the circle, inside the disc |I - Ic| <= Irad, over the whole
//    edge (tau sub-intervals, bisected adaptively) x the k-box; and again after EVERY step on its whole-step enclosure.
//  * After EVERY step: every enclosure finite, and z^2 + a^2 != 0, G1 != 0, G2 != 0 certified on the WHOLE-STEP
//    enclosure (getLastEnclosure, with z over the step's whole time interval). Any failure REFUSES: the output says
//    REFUSED and the exit code is 2. Exceptions from CAPD (after the dyadic retries) also refuse.
//  * Exact time (C2-4 (b)): the driver's own step loop. maxStep = the EXACT remainder of the edge; a CAPD exception
//    halves it (dyadic) down to 2^-40; after every step the set's time must be a POINT; the edge ends exactly at j + 1.
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

static const int DIM = 14, NPAR = 8;
static int SFORM = 0;          // 0 disc: s = sqrt_p(B); 1 circle: s = w sqrt_p(I)
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

static double mag(const IT& x) {   // for the log only
  return std::max(std::fabs(dbl(x.leftBound())), std::fabs(dbl(x.rightBound())));
}

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

// principal root: re = sqrt((|A| + Re A)/2), im = Im A / (2 re)   (continuous off the cut (-inf, 0])
template <class T> Cx<T> csqrt_p(const Cx<T>& A, const T& half, const T& two) {
  T m = sqrt(A.re * A.re + A.im * A.im);
  T re = sqrt((m + A.re) * half);
  return {re, A.im / (re * two)};
}
// the root's argument: B (disc) or I (circle); w = z^2/a^2
template <class T> Cx<T> rootArg(const Cx<T>& w, const Cx<T>& k, const T& c90, const T& c21, const T& c60, const T& c18,
                                 const T& c10, const T& one) {
  Cx<T> c2 = {c90 - c21 * k.re, -(c21 * k.im)};
  Cx<T> c1 = {c18 * k.re - c60, c18 * k.im};
  Cx<T> cc = {c10 - k.re, -k.im};
  if (SFORM == 0) return c2 * w * w + c1 * w + cc;
  Cx<T> iw = Cx<T>{one, one - one} / w;
  return c2 + c1 * iw + cc * iw * iw;
}
template <class T> Cx<T> sOf(const Cx<T>& w, const Cx<T>& A, const T& half, const T& two) {
  Cx<T> r = csqrt_p(A, half, two);
  return SFORM == 0 ? r : w * r;
}

// ------------------------------------------------------------------------------------------------ the vector field
// params: 0 a | 1 E2 | 2 pref | 3 Re P_j | 4 Im P_j | 5 Re h_j | 6 Im h_j | 7 t_j (= j)
void field(Node t, Node in[], int, Node out[], int, Node par[], int) {
  Node two(2.0), zero(0.0), half(0.5), one(1.0), c90(90.0), c21(21.0), c60(60.0), c18(18.0), c10(10.0);
  Node a = par[0], E2 = par[1], pref = par[2];
  Cx<Node> h = {par[5], par[6]};
  Cx<Node> z = {par[3] + (t - par[7]) * par[5], par[4] + (t - par[7]) * par[6]};
  Cx<Node> c0 = {in[0], in[1]}, c0p = {in[2], in[3]};
  Cx<Node> y00 = {in[4], in[5]}, y01 = {in[6], in[7]}, y10 = {in[8], in[9]}, y11 = {in[10], in[11]};
  Cx<Node> k = {in[12], in[13]};
  Node a2 = a * a;
  Cx<Node> z2 = z * z;
  Cx<Node> w = {z2.re / a2, z2.im / a2};
  Cx<Node> A = rootArg(w, k, c90, c21, c60, c18, c10, one);
  Cx<Node> s = sOf(w, A, half, two);
  Q<Node> qq = quants(z, c0, c0p, a, E2, two, zero);
  Cx<Node> D3 = qq.D * qq.D * qq.D;
  Cx<Node> dc0p = scale(s, pref) / D3;
  Cx<Node> lam = qq.dG1 / qq.G1 - qq.dG2 / qq.G2;
  Cx<Node> q = scale(lam * lam, Node(0.1875));
  Cx<Node> mq = {-q.re, -q.im};
  Cx<Node> d[6] = {c0p, dc0p, y10, y11, mq * y00, mq * y01};
  for (int i = 0; i < 6; ++i) {
    Cx<Node> o = h * d[i];
    out[2 * i] = o.re;
    out[2 * i + 1] = o.im;
  }
  out[12] = in[12] * 0.0;
  out[13] = in[13] * 0.0;
}

// the root guards on (z-box, k-box): (a1) lower(|A| + Re A) > 0; (a2, circle) |I - Ic|^2 <= Irad^2.  0 = ok, else 1 / 2
static Cx<IT> ICc;
static IT IRAD2;
static double LASTA1 = 0;       // log only (C2-M H2 record): the certified lower bound of |A| + Re A at the last guard call
static int rootGuard(const Cx<IT>& z, const Cx<IT>& k, const IT& a) {
  IT one(1), half(0.5), two(2), c90(90), c21(21), c60(60), c18(18), c10(10);
  IT a2 = a * a;
  Cx<IT> z2 = z * z;
  Cx<IT> w = {z2.re / a2, z2.im / a2};
  Cx<IT> A = rootArg(w, k, c90, c21, c60, c18, c10, one);
  IT m = sqrt(sqr(A.re) + sqr(A.im));
  IT g = m + A.re;
  LASTA1 = finiteI(g) ? dbl(g.leftBound()) : -1.0;
  if (!finiteI(g) || !(g.leftBound() > 0)) return 1;
  if (SFORM == 1) {
    IT d2 = sqr(A.re - ICc.re) + sqr(A.im - ICc.im);
    if (!finiteI(d2) || !(d2.rightBound() <= IRAD2.leftBound())) return 2;
  }
  return 0;
}
// a priori over a whole edge: tau in [lo, hi] (sub-interval of [0, 1]) bisected adaptively
static int edgeGuard(const IT& P0re, const IT& P0im, const IT& hre, const IT& him, const Cx<IT>& K, const IT& a,
                     const IT& lo, const IT& hi, int depth) {
  IT T(lo.leftBound(), hi.rightBound());
  Cx<IT> z = {P0re + T * hre, P0im + T * him};
  int g = rootGuard(z, K, a);
  if (g == 0) return 0;
  if (depth == 0) return g;
  IT mid = (lo + hi) / IT(2);
  int g1 = edgeGuard(P0re, P0im, hre, him, K, a, lo, mid, depth - 1);
  if (g1) return g1;
  return edgeGuard(P0re, P0im, hre, him, K, a, mid, hi, depth - 1);
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
  std::string sform;
  in >> tag >> sform;
  if (tag != "sform" || (sform != "disc" && sform != "circle")) die("input: expected sform disc|circle");
  SFORM = (sform == "circle") ? 1 : 0;
  in >> tag;
  if (tag != "Ic") die("input: expected Ic");            // the circle's inner-disc centre (ignored for disc)
  ICc.re = readPoint(in);
  ICc.im = readPoint(in);
  in >> tag;
  if (tag != "Irad") die("input: expected Irad");
  IT Irad = readPoint(in);
  IRAD2 = Irad * Irad;
  int plantTime;
  in >> tag >> plantTime;
  if (tag != "plant_time") die("input: expected plant_time");
  int skipEdgeGuard;                     // read F2: 1 only in controls K2s, K3s (the per-step guard must then fire)
  in >> tag >> skipEdgeGuard;
  if (tag != "skip_edge_guard") die("input: expected skip_edge_guard");
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
  const int K0 = 12, K1 = 13;
  VecT x(DIM), r0(DIM), rv(DIM);
  MatT C(DIM, DIM);
  in >> tag;
  if (tag != "x") die("input: expected x");
  for (int i = 0; i < DIM; ++i) x[i] = readPoint(in);
  in >> tag;
  if (tag != "C") die("input: expected C");
  for (int i = 0; i < DIM; ++i) {
    for (int j = 0; j < DIM; ++j) C[i][j] = IT(0);
    C[i][K0] = readPoint(in);
    C[i][K1] = readPoint(in);
  }
  in >> tag;
  if (tag != "r") die("input: expected r");
  for (int i = 0; i < DIM; ++i) {
    capd::MpFloat ri = readF(in);
    if (ri < 0) die("input: negative radius");
    rv[i] = IT(-ri, ri);
    r0[i] = IT(0);
  }
  r0[K0] = IT(-R, R);
  r0[K1] = IT(-R, R);
  // read F3: Kbox = x + r0 is the k sub-box only if the k rows of C are the identity and their radii are 0
  for (int jj = 0; jj < DIM; ++jj) {
    if (jj == K0 || jj == K1) continue;
    if (!(C[K0][jj] == IT(0)) || !(C[K1][jj] == IT(0))) die("input: k rows of C not the identity");
  }
  if (!(C[K0][K0] == IT(1)) || !(C[K0][K1] == IT(0)) || !(C[K1][K0] == IT(0)) || !(C[K1][K1] == IT(1)))
    die("input: k rows of C not the identity");
  if (!(rv[K0] == IT(0)) || !(rv[K1] == IT(0))) die("input: k radii not 0");
  Cx<IT> Kbox = {x[K0] + r0[K0], x[K1] + r0[K1]};       // the k sub-box (the k-states are exactly kc0 + r0)
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
  out << "c2_driver prec " << PREC << " order " << order << " dim " << DIM << " policy " << POLICY << " sform "
      << sform << " plant_time " << plantTime << " skip_edge_guard " << skipEdgeGuard << "\n";
  slog << "loop edge step t dt min|D|^2 min|G1|^2 min|G2|^2 maxdiam | c0 c0p Y widths | retries\n";
  IT two(2), zero(0), half(0.5);
  const capd::MpFloat MINSTEP = capd::MpFloat(1) / capd::MpFloat(1099511627776.0);   // 2^-40, exact
  // CAPD's first step after an (re)initialisation is min(1/Lipschitz, 1, maxStep), and 1/Lipschitz has a full
  // mantissa. Later steps come from clearMantissaBits (5-bit dyadics), maxStep, or exact rescalings (step*0.95,
  // step*factor in the enclosure approval). CAPD re-initialises at a loop's start, after a retry and at new edges, so
  // a FRESH step (every edge start, and after a retry) gets maxStep capped at the dyadic 2^-6. The step after a fresh one
  // is limited to twice the previous step (read F4), so the cap costs a few short steps per edge, not one. Exactness is
  // never assumed: the point check and the end check refuse any inexact time.
  const capd::MpFloat FIRSTCAP = capd::MpFloat(1) / capd::MpFloat(64.0);

  MapT vf(field, DIM, DIM, NPAR);
  vf.setParameter(0, a);
  vf.setParameter(1, E2);
  vf.setParameter(2, pref);
  SolverT solver(vf, order);
  solver.setAbsoluteTolerance(tol);
  solver.setRelativeTolerance(tol);

  auto refuse = [&](int l, size_t j, long n, const std::string& why) {
    slog << "REFUSED " << why << "\n";
    slog.flush();
    out << "REFUSED loop " << l << " edge " << j << " step " << n << " " << why << "\n";
    out.flush();
    std::exit(2);
  };
  auto isPoint = [](const IT& t) { return t.leftBound() == t.rightBound(); };
  bool planted = false;

  for (int l = 0; l < nloops; ++l) {
    SetT set(x, C, r0, rv, IT(0));
    long nsteps = 0;
    double dtmin = 1e300, dtmax = 0;
    const auto& P = loops[l];
    bool fresh = true;
    solver.clearCoefficients();
    for (size_t j = 0; j + 1 < P.size(); ++j) {
      IT hre = P[j + 1].first - P[j].first, him = P[j + 1].second - P[j].second;
      if (!isPoint(hre) || !isPoint(him)) refuse(l, j, nsteps, "edge vector not exact");
      // (a1), (a2) a priori over the whole edge x the k-box (tau bisected up to depth 10)
      int g = skipEdgeGuard ? 0 : edgeGuard(P[j].first, P[j].second, hre, him, Kbox, a, IT(0), IT(1), 10);
      if (g == 1) refuse(l, j, nsteps, "(a1) root argument not certified off the cut on this edge");
      if (g == 2) refuse(l, j, nsteps, "(a2) circle inner argument not certified inside its disc on this edge");
      IT tj((double)j);
      solver.getVectorField().setParameter(3, P[j].first);
      solver.getVectorField().setParameter(4, P[j].second);
      solver.getVectorField().setParameter(5, hre);
      solver.getVectorField().setParameter(6, him);
      solver.getVectorField().setParameter(7, tj);
      const capd::MpFloat tf = capd::MpFloat((double)(j + 1));
      IT t = set.getCurrentTime();
      if (!isPoint(t) || !(t.leftBound() == tj.leftBound())) refuse(l, j, nsteps, "(b) edge start time not exactly j");
      fresh = true;
      while (t.leftBound() < tf) {
        SetT stepBackup = set;                                     // the state at t, for an exactness rollback
        IT cap = IT(FIRSTCAP);
        IT maxStep, tcur;
        int retries = 0, exactRetries = 0;
        for (;;) {                                                 // until a step lands on a time with an exact
          maxStep = IT(tf) - t;                                    // remainder (or exactly on tf)
          if (!isPoint(maxStep)) refuse(l, j, nsteps, "(b) edge remainder not exact");
          if (fresh && maxStep.leftBound() > cap.leftBound()) maxStep = cap;
          for (;;) {
            SetT backup = set;                                      // read F1: CAPD may advance parts of the set
            try {                                                   // before throwing; a retry must start from t
              solver.setMaxStep(maxStep);
              solver(set);
              fresh = false;
              break;
            } catch (std::exception& e) {
              set = backup;
              if (!(set.getCurrentTime() == t)) refuse(l, j, nsteps, "(b) the restored set's time is not t");
              solver.clearCoefficients();
              fresh = true;
              maxStep = maxStep / two;                              // exact halving
              if (maxStep.leftBound() > cap.leftBound()) maxStep = cap;
              ++retries;
              if (maxStep.rightBound() < MINSTEP)
                refuse(l, j, nsteps, std::string("capd exception below the minimal step: ") + e.what());
            }
          }
          if (plantTime) {                                         // control (K4, erratum E2): a non-point time
            set.setCurrentTime(set.getCurrentTime() + IT(capd::MpFloat(0), MINSTEP * MINSTEP));   // on EVERY attempt
            planted = true;
          }
          tcur = set.getCurrentTime();
          if (isPoint(tcur) && isPoint(IT(tf) - tcur)) break;      // an exact time with an exact remainder: accept
          // erratum E2: a non-point time (CAPD's inexact rescalings, e.g. step*0.95 repeated) or a point time whose
          // remainder is not representable (a full-mantissa first step) is NEVER accepted: roll back to t and retry
          // as a fresh step whose cap is a power of two at most half the step just taken (CAPD then takes the cap
          // exactly unless it must shrink it); refuse below the minimal step
          IT taken = tcur - t;
          set = stepBackup;
          if (!(set.getCurrentTime() == t)) refuse(l, j, nsteps, "(b) the rolled-back set's time is not t");
          solver.clearCoefficients();
          fresh = true;
          {
            mpfr_srcptr tp = MpAcc::get(taken.leftBound());
            capd::MpFloat nc = cap.leftBound() / capd::MpFloat(4);
            if (mpfr_number_p(tp) && mpfr_sgn(tp) > 0) {
              capd::MpFloat p2 = capd::MpFloat(1);                  // 2^(exp(taken) - 2) <= taken/2
              mpfr_mul_2si(MpAcc::mut(p2), MpAcc::get(p2), (long)mpfr_get_exp(tp) - 2, MPFR_RNDN);
              if (p2 < nc) nc = p2;
            }
            cap = IT(nc);
          }
          ++exactRetries;
          if (cap.rightBound() < MINSTEP)
            refuse(l, j, nsteps, "(b) no step with an exact time above the minimal step (last time " + exI(tcur) + ")");
        }
        ++nsteps;
        const VecT& E = set.getLastEnclosure();
        VecT hull = (VecT)set;
        bool fin = true;
        for (int i = 0; i < DIM; ++i) fin = fin && finiteI(E[i]) && finiteI(hull[i]);
        IT T = IT(t.leftBound(), tcur.rightBound()) - tj;
        Cx<IT> z = {P[j].first + T * hre, P[j].second + T * him};
        Cx<IT> kE = {E[K0], E[K1]};
        int gs = rootGuard(z, kE, a);
        if (gs == 1) refuse(l, j, nsteps, "(a1) root argument not certified off the cut on the whole-step enclosure");
        if (gs == 2) refuse(l, j, nsteps, "(a2) circle inner argument not inside its disc on the whole-step enclosure");
        Cx<IT> c0 = {E[0], E[1]}, c0p = {E[2], E[3]};
        Q<IT> qq = quants(z, c0, c0p, a, E2, two, zero);
        IT mD = abs2(qq.D), m1 = abs2(qq.G1), m2 = abs2(qq.G2);
        bool dom = fin && finiteI(mD) && finiteI(m1) && finiteI(m2) && mD.leftBound() > 0 && m1.leftBound() > 0 &&
                   m2.leftBound() > 0;
        double dt = dbl(tcur.rightBound()) - dbl(t.leftBound());
        dtmin = std::min(dtmin, dt);
        dtmax = std::max(dtmax, dt);
        auto bw = [&](int a0, int a1) {
          double w = 0;
          for (int i = a0; i <= a1; ++i) w = std::max(w, dbl(diam(hull[i]).rightBound()));
          return w;
        };
        slog << l << " " << j << " " << nsteps << " " << dbl(tcur.rightBound()) << " " << dt << " "
             << dbl(mD.leftBound()) << " " << dbl(m1.leftBound()) << " " << dbl(m2.leftBound()) << " " << bw(0, DIM - 1)
             << " | " << bw(0, 1) << " " << bw(2, 3) << " " << bw(4, 11) << " | " << retries << " " << exactRetries
             << " | a1 " << LASTA1 << "\n";
        if (!dom)
          refuse(l, j, nsteps, fin ? "domain (z^2 + a^2, G1, G2) not certified on the whole-step enclosure"
                                   : "non-finite enclosure");
        t = tcur;
      }
      if (!(isPoint(t) && t.leftBound() == tf)) refuse(l, j, nsteps, "(b) the edge did not end exactly at j + 1");
    }
    const VecT& sx = set.get_x();
    const MatT& sC = set.get_C();
    VecT Br = set.get_B() * set.get_r();
    VecT hull = (VecT)set;
    out << "loop " << l << " steps " << nsteps << " dtmin " << dtmin << " dtmax " << dtmax << "\n";
    for (int i = 0; i < DIM; ++i) {
      // C r0 with r0 zero off the k components: only columns K0, K1 enter (r0 is asserted unchanged)
      if (!(set.get_r0()[i] == r0[i])) die("r0 changed during the integration");
      out << "row " << i << " x " << exI(sx[i]) << " ckr " << exI(sC[i][K0]) << " cki " << exI(sC[i][K1]) << " br "
          << exI(Br[i]) << " hull " << exI(hull[i]) << "\n";
    }
  }
  out << "DONE\n";
  return 0;
}
