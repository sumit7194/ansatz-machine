# C2-M non-author read (registration order step 3), 2026-11-28
**Reader:** a fresh agent (not the author). Read-only, with import-only checks and no CAPD. It read 199f9cf; the
re-reads covered 199f9cf..07e6f75 and 07e6f75..9d9390f.

## First read (199f9cf): no path to a false certificate, but four majors
- **F1, major:** the node-precision assertion was wrong for the traces (by construction), so M4 tested nothing.
  Fixed by erratum C2-M-2: the assertion is for F only.
- **F2, major:** a cell's record was not tied to its run. Fixed: a nonce, the exact geometry, delete-before-launch.
- **F3:** M2 was one combined plant. Fixed: three plants, using ellipse samples only, with separate files.
- **F4, major:** M1's records could be stale. Fixed: stamped, and all 81 asserted.
- **F5, major:** the driver binary was not in the hash. Fixed: its bytes are in CODE, and IdQR is checked.
- **F6, minor:** the cover gate re-read the same file. Fixed: M is recomputed from the leaves.
- **F7, minor:** M3 did not exercise accept()'s branches. Fixed: five dry modes.
- **F8, minor:** no MODE assert. Fixed.
- Verified by the reader: both substitution texts match once; CODE, NODEF and VJSON carry the c2m BASE; the me()
  round trip is exact; the quadrants are exact; the driver's log columns are parsed right; and the margins are
  reported only (certification rests on the driver's refusals and rc).

## Re-read 1 (199f9cf..07e6f75)
- **PASS:** F1–F5, F7, F8, and the restoration of verdict_c2m and make_proof.
- **F6: FAIL (major, fail-closed).** The gate compared a printed-and-parsed ball's lower end, which refused every real
  cover; and its geometry check was vacuous. **Fixed at 9d9390f:** it compares par_up against the sup's upper end,
  and re-checks each record's own nonce and cell string.

## Re-read 2 (07e6f75..9d9390f): PASS
- The direction is correct, and the verdict applies par_up of the same string.
- run_id and cell are stored and checked; a legitimate cover matches.
