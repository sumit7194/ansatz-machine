# C2-TM controls T3–T5 (the registration; T1 and T2 run inside the probe), 2026-11-28, on P2
Runner: `scripts/_nve_c2tm_controls.py`; records in `c2/c2tm_P2_T{3,4,5}.json`.

**T4: PASS.** The start TMs' first and second coefficients (c0 and c0') agree with V1's central differences within the
METHOD's tolerance. The first-coefficient tolerance is about 8e-5 for c0 and 5e-5 for c0'; the second, about 7e-4 and
4e-4. sup|f'''| and sup|f''''| come from a separate rectangle-rule enclosure of the explicit k-derivatives. The x1.01
plant was caught for both.

**T3: PASS on the registered criterion; the script's stricter string not met (recorded both ways, accepted by the
Bridge).** With a planted c0 remainder, q_on_box was refused by "reciprocal theta-guard (G1 on the box): theta 5.42 >
1/2". The registration asks for "the reciprocal's theta-guard, not an incidental one", and that holds. The script's
expected string named G2, but q_on_box evaluates G1's reciprocal first. The unplanted q_on_box passes.

**T5: FIRED.**
- The first run crashed in the control's own zero selection: it evaluated the floats points as rounded doubles, where
  |G2| is about 1e-16. Fixed to use the exact strings (b02a2ee), and the fix passed a non-author glance on all three
  points.
- The glance's minor concern: the constant-coefficient refusal was unnamed. Fixed at cf25d66: it is named, and T5 now
  counts only a refusal naming G2.
- The rerun (run on the pre-cf25d66 core) was refused: "no admissible step at 1.78798+0.13056i (last refusal:
  reciprocal theta-guard (G2 on the box): theta 0.5 > 1/2)". That is the NAMED G2 theta-guard, so it counts
  unambiguously. The printed 0.5 is a theta just above one half, rounded for display.
