#!/bin/bash
# The local gate: every battery, both directions (knowns pass, sabotage
# fails), one verdict. Run before any "done" claim.
cd "$(dirname "$0")" || exit 1
PY=.venv/bin/python

declare -a NAMES CMDS
NAMES+=("01 verifier (+Kerr)");   CMDS+=("scripts/01_verifier.py --kerr")
NAMES+=("02 fingerprints");       CMDS+=("scripts/02_fingerprints.py")
NAMES+=("03 rediscovery");        CMDS+=("scripts/03_rediscover.py")
NAMES+=("04 campaign");           CMDS+=("scripts/04_campaign.py")
[ -f scripts/05_generalize.py ] && { NAMES+=("05 catalog growth"); CMDS+=("scripts/05_generalize.py"); }
[ -f scripts/06_two_function.py ] && { NAMES+=("06 two-function hall"); CMDS+=("scripts/06_two_function.py --quick"); }
[ -f scripts/07_expedition.py ] && { NAMES+=("07 expedition"); CMDS+=("scripts/07_expedition.py"); }
[ -f scripts/08_stationary.py ] && { NAMES+=("08 stationary hall"); CMDS+=("scripts/08_stationary.py --quick"); }
[ -f scripts/10_edgb_reduce.py ] && { NAMES+=("10 EdGB E0 (vs Kanti)"); CMDS+=("scripts/10_edgb_reduce.py"); }
[ -f scripts/21_rot_fingerprint.py ] && { NAMES+=("21 rotating fingerprint"); CMDS+=("scripts/21_rot_fingerprint.py"); }
[ -f scripts/22_rot_fit.py ] && { NAMES+=("22 rotating fit (banked-formula verify)"); CMDS+=("scripts/22_rot_fit.py"); }
[ -f scripts/sealed_holdout.py ] && { NAMES+=("SH sealed-holdout guard"); CMDS+=("scripts/sealed_holdout.py"); }
[ -f scripts/24_abstractor.py ] && { NAMES+=("24 abstractor (recovers Tangherlini law)"); CMDS+=("scripts/24_abstractor.py"); }
[ -f scripts/26_information_meter.py ] && { NAMES+=("26 information meter (hair counter)"); CMDS+=("scripts/26_information_meter.py"); }
[ -f scripts/27_scalar.py ] && { NAMES+=("27 scalar source (sanity)"); CMDS+=("scripts/27_scalar.py"); }
[ -f scripts/28_maxwell.py ] && { NAMES+=("28 maxwell source (RN)"); CMDS+=("scripts/28_maxwell.py"); }
[ -f scripts/29_matter_meter.py ] && { NAMES+=("29 matter meter (RN hair=2)"); CMDS+=("scripts/29_matter_meter.py"); }
[ -f scripts/30_dilaton.py ] && { NAMES+=("30 dilaton (secondary hair)"); CMDS+=("scripts/30_dilaton.py"); }
[ -f scripts/31_matter_hunt.py ] && { NAMES+=("31 matter discovery (RN)"); CMDS+=("scripts/31_matter_hunt.py"); }
[ -f scripts/32_no_hair.py ] && { NAMES+=("32 no-hair (proven + searched)"); CMDS+=("scripts/32_no_hair.py"); }
[ -f scripts/33_no_hair_ladder.py ] && { NAMES+=("33 no-hair ladder (structural, any n,Λ)"); CMDS+=("scripts/33_no_hair_ladder.py"); }
[ -f scripts/34_hair_criterion.py ] && { NAMES+=("34 hair criterion (no-hair⇔angular source)"); CMDS+=("scripts/34_hair_criterion.py"); }
[ -f scripts/35_thermodynamics.py ] && { NAMES+=("35 thermodynamics (recovers S=A/4, first law)"); CMDS+=("scripts/35_thermodynamics.py"); }
[ -f scripts/36_energy_conditions.py ] && { NAMES+=("36 energy conditions (physicality classifier)"); CMDS+=("scripts/36_energy_conditions.py"); }
[ -f scripts/37_cosmology.py ] && { NAMES+=("37 cosmology (Friedmann + expansion law)"); CMDS+=("scripts/37_cosmology.py"); }
[ -f scripts/38_exotic_spacetimes.py ] && { NAMES+=("38 exotic spacetimes (wormhole/warp need exotic matter)"); CMDS+=("scripts/38_exotic_spacetimes.py"); }
[ -f scripts/40_analyzer.py ] && { NAMES+=("40 general analyzer (one tool, the whole zoo)"); CMDS+=("scripts/40_analyzer.py"); }
[ -f scripts/41_atlas.py ] && { NAMES+=("41 atlas (12 spacetimes incl. Kerr & Gödel)"); CMDS+=("scripts/41_atlas.py"); }
[ -f scripts/42_causal_structure.py ] && { NAMES+=("42 causal structure (spacelike vs timelike singularity)"); CMDS+=("scripts/42_causal_structure.py"); }
[ -f scripts/43_discover.py ] && { NAMES+=("43 discovery (invents Schwarzschild, survivable, de Sitter, exotic)"); CMDS+=("scripts/43_discover.py --quick"); }
[ -f scripts/44_discover_rotating.py ] && { NAMES+=("44 rotating discovery (rediscovers Kerr + Kerr-Newman)"); CMDS+=("scripts/44_discover_rotating.py --quick"); }
[ -f scripts/45_observables.py ] && { NAMES+=("45 observables (photon sphere + EHT shadow)"); CMDS+=("scripts/45_observables.py"); }
[ -f scripts/46_numeric_curvature.py ] && { NAMES+=("46 numeric curvature (verifies Kerr-de Sitter)"); CMDS+=("scripts/46_numeric_curvature.py"); }
[ -f scripts/47_kasner.py ] && { NAMES+=("47 Kasner (recovers Σp=1, Σp²=1 anisotropic-vacuum law)"); CMDS+=("scripts/47_kasner.py"); }
[ -f scripts/48_ring_singularity.py ] && { NAMES+=("48 ring singularity (numeric Kretschmann, Kerr ring)"); CMDS+=("scripts/48_ring_singularity.py"); }
[ -f scripts/49_light_bending.py ] && { NAMES+=("49 light bending (1919 Eddington test)"); CMDS+=("scripts/49_light_bending.py"); }
[ -f scripts/50_precession.py ] && { NAMES+=("50 perihelion precession (Mercury test, diverges at ISCO)"); CMDS+=("scripts/50_precession.py"); }
[ -f scripts/51_redshift.py ] && { NAMES+=("51 gravitational redshift (Pound-Rebka, third classic test)"); CMDS+=("scripts/51_redshift.py"); }
[ -f scripts/52_stellar_structure.py ] && { NAMES+=("52 stellar structure (recovers TOV — the engine builds a star)"); CMDS+=("scripts/52_stellar_structure.py"); }
[ -f scripts/53_buchdahl.py ] && { NAMES+=("53 Buchdahl bound (max star compactness M/R=4/9)"); CMDS+=("scripts/53_buchdahl.py"); }
[ -f scripts/54_mass_radius.py ] && { NAMES+=("54 mass-radius (max neutron-star mass, Oppenheimer-Volkoff)"); CMDS+=("scripts/54_mass_radius.py"); }
[ -f scripts/55_analyzer_star.py ] && { NAMES+=("55 analyzer reaches a star (general tool, honest boundary)"); CMDS+=("scripts/55_analyzer_star.py"); }
[ -f scripts/56_ringdown.py ] && { NAMES+=("56 ringdown (exact wave potential + eikonal QNM from the metric)"); CMDS+=("scripts/56_ringdown.py"); }
[ -f scripts/57_petrov.py ] && { NAMES+=("57 Petrov type (Weyl algebra: black holes=D, waves=N, flat=O)"); CMDS+=("scripts/57_petrov.py"); }
[ -f scripts/58_killing.py ] && { NAMES+=("58 Killing symmetries (SO(3) + Kerr's hidden Carter constant)"); CMDS+=("scripts/58_killing.py"); }
[ -f scripts/59_tidal.py ] && { NAMES+=("59 tidal forces (spaghettification, real-vs-coordinate singularity)"); CMDS+=("scripts/59_tidal.py"); }
[ -f scripts/60_frame_dragging.py ] && { NAMES+=("60 frame dragging (ergosphere, Lense-Thirring, Penrose)"); CMDS+=("scripts/60_frame_dragging.py"); }
[ -f scripts/61_kerr_thermo.py ] && { NAMES+=("61 Kerr thermodynamics (rotating-horizon T/S, Smarr, first law)"); CMDS+=("scripts/61_kerr_thermo.py"); }
[ -f scripts/62_komar.py ] && { NAMES+=("62 Komar charges (mass & spin as symmetry charges)"); CMDS+=("scripts/62_komar.py"); }
[ -f scripts/63_embedding.py ] && { NAMES+=("63 embedding (Flamm paraboloid, proper distance, the throat)"); CMDS+=("scripts/63_embedding.py"); }
[ -f scripts/64_cosmological_horizon.py ] && { NAMES+=("64 cosmological horizon (de Sitter Gibbons-Hawking T, S)"); CMDS+=("scripts/64_cosmological_horizon.py"); }
[ -f scripts/65_raychaudhuri.py ] && { NAMES+=("65 Raychaudhuri focusing (SEC -> singularity, the dark-energy escape)"); CMDS+=("scripts/65_raychaudhuri.py"); }
[ -f scripts/66_effective_potential.py ] && { NAMES+=("66 effective potential (ISCO/photon sphere as a well; the GR term)"); CMDS+=("scripts/66_effective_potential.py"); }
[ -f scripts/67_lensing.py ] && { NAMES+=("67 gravitational lensing (Einstein ring, double images, microlensing)"); CMDS+=("scripts/67_lensing.py"); }
[ -f scripts/68_kerr_shadow.py ] && { NAMES+=("68 Kerr shadow (split light ring, asymmetric D-shaped shadow)"); CMDS+=("scripts/68_kerr_shadow.py"); }
[ -f scripts/69_killing_yano.py ] && { NAMES+=("69 Killing-Yano (root of the Carter constant: K=Y.Y)"); CMDS+=("scripts/69_killing_yano.py"); }
[ -f scripts/70_hawking_spectrum.py ] && { NAMES+=("70 Hawking spectrum (greybody, negative heat capacity, M^3 lifetime)"); CMDS+=("scripts/70_hawking_spectrum.py"); }
[ -f scripts/71_adm.py ] && { NAMES+=("71 ADM 3+1 (Friedmann = the Hamiltonian constraint)"); CMDS+=("scripts/71_adm.py"); }
[ -f scripts/72_ringdown_template.py ] && { NAMES+=("72 ringdown template (no-hair spectroscopy, Q=l/(2n+1))"); CMDS+=("scripts/72_ringdown_template.py"); }
[ -f scripts/73_inspiral_chirp.py ] && { NAMES+=("73 inspiral chirp (chirp mass, (t_c-t)^-3/8 sweep)"); CMDS+=("scripts/73_inspiral_chirp.py"); }
[ -f scripts/74_gw_polarizations.py ] && { NAMES+=("74 GW polarizations (spin-2 +/x, the 2-vs-6 modes-of-gravity test)"); CMDS+=("scripts/74_gw_polarizations.py"); }
[ -f scripts/75_area_theorem.py ] && { NAMES+=("75 area theorem (2nd law; merger energy budget, consistency oracle)"); CMDS+=("scripts/75_area_theorem.py"); }
[ -f scripts/76_invariant_fingerprint.py ] && { NAMES+=("76 invariant fingerprint (coordinate-free signature; learned-geometry oracle)"); CMDS+=("scripts/76_invariant_fingerprint.py"); }
[ -f scripts/77_qnm_precise.py ] && { NAMES+=("77 precise QNM oracle (Leaver/qnm; 0.1% ringdown, the 221 overtone)"); CMDS+=("scripts/77_qnm_precise.py"); }
[ -f scripts/78_killing_tensor_proof.py ] && { NAMES+=("78 symbolic Killing-tensor proof (Carter constant, exact)"); CMDS+=("scripts/78_killing_tensor_proof.py"); }
[ -f scripts/79_geodesic_chaos.py ] && { NAMES+=("79 geodesic + chaos lens (Kerr regular vs di-hole chaotic)"); CMDS+=("scripts/79_geodesic_chaos.py"); }
[ -f scripts/80_petrov_kerr.py ] && { NAMES+=("80 Petrov type of Kerr (numeric: type D, completes §57)"); CMDS+=("scripts/80_petrov_kerr.py"); }
[ -f scripts/81_analyzer_audit.py ] && { NAMES+=("81 analyzer robustness audit (verdicts vs ground truth)"); CMDS+=("scripts/81_analyzer_audit.py"); }
[ -f scripts/82_integrability_frontier.py ] && { NAMES+=("82 integrability frontier (deform Kerr: Carter tensor fails, no visible chaos, fate open)"); CMDS+=("scripts/82_integrability_frontier.py"); }
[ -f scripts/83_tetradfree_type.py ] && { NAMES+=("83 tetrad-free Weyl invariants I,J (coordinate-free speciality; Kerr type D off-diagonal)"); CMDS+=("scripts/83_tetradfree_type.py"); }
[ -f scripts/84_poincare_integrability.py ] && { NAMES+=("84 Poincaré integrability lens (Kerr tori; deformation regular-or-destroyed, no bounded chaos)"); CMDS+=("scripts/84_poincare_integrability.py"); }
[ -f scripts/85_no_carter_under_deformation.py ] && { NAMES+=("85 no Carter under deformation (numeric: recovers Kerr Carter, deformed has none -> non-integrable)"); CMDS+=("scripts/85_no_carter_under_deformation.py"); }
[ -f scripts/86_kerr_observables.py ] && { NAMES+=("86 Kerr observables (ISCO 6M->M/9M; full EHT shadow silhouette circle->D-shape)"); CMDS+=("scripts/86_kerr_observables.py"); }
[ -f scripts/87_observe_any_rotating.py ] && { NAMES+=("87 observe any rotating BH (numeric photon ring/shadow/ISCO; Kerr-Newman & deformed distinct)"); CMDS+=("scripts/87_observe_any_rotating.py"); }
[ -f scripts/88_three_messengers.py ] && { NAMES+=("88 three messengers (shadow EHT + ISCO X-ray + ringdown LIGO; complementary discrimination)"); CMDS+=("scripts/88_three_messengers.py"); }
[ -f scripts/89_photon_subrings.py ] && { NAMES+=("89 photon subrings (Schwarzschild gamma=pi; same lambda in EHT subrings & LIGO ringdown)"); CMDS+=("scripts/89_photon_subrings.py"); }
[ -f scripts/90_black_hole_or_imposter.py ] && { NAMES+=("90 black hole or imposter (wormhole fakes shadow; naked singularity breaks it; shadow != horizon)"); CMDS+=("scripts/90_black_hole_or_imposter.py"); }
[ -f scripts/91_shadow_inclination.py ] && { NAMES+=("91 shadow inclination (asymmetry scales with tilt; face-on->circular; spin-inclination degeneracy)"); CMDS+=("scripts/91_shadow_inclination.py"); }
[ -f scripts/92_accretion_engine.py ] && { NAMES+=("92 accretion engine (efficiency 5.7%->42%; smaller ISCO=hotter; spin->ISCO->X-ray continuum)"); CMDS+=("scripts/92_accretion_engine.py"); }
[ -f scripts/93_weigh_spin_three_ways.py ] && { NAMES+=("93 weigh spin 3 ways (Kerr consistent; charge degenerate; near-horizon deformation caught -- null test of no-hair)"); CMDS+=("scripts/93_weigh_spin_three_ways.py"); }
[ -f scripts/94_precession_qpos.py ] && { NAMES+=("94 precession & QPOs (nu_r=0 at ISCO; periastron+nodal Lense-Thirring; matches kHz-QPO band)"); CMDS+=("scripts/94_precession_qpos.py"); }
[ -f scripts/95_strong_lensing.py ] && { NAMES+=("95 strong lensing (weak->4M/b; strong log-divergence a=1; a=Omega_c/lambda, a*gamma=pi)"); CMDS+=("scripts/95_strong_lensing.py"); }
[ -f scripts/96_tidal_forces.py ] && { NAMES+=("96 tidal forces (E_rr=-2M/r^3 spaghettification; horizon tidal ~1/M^2; Hills mass; BH Love number=0)"); CMDS+=("scripts/96_tidal_forces.py"); }
[ -f scripts/97_zipoy_voorhees_integrability.py ] && { NAMES+=("97 Zipoy-Voorhees (exact vacuum quadrupole BH; recovers Carter at delta=1, no conserved quadratic for delta!=1; validates 85)"); CMDS+=("scripts/97_zipoy_voorhees_integrability.py"); }
[ -f scripts/98_quartic_killing_tensor.py ] && { NAMES+=("98 no quartic Killing tensor either (delta=1 recovers K and K^2; delta!=1 has no rank-2 or rank-4 invariant; closes 97's caveat)"); CMDS+=("scripts/98_quartic_killing_tensor.py"); }
[ -f scripts/99_manko_novikov_integrability.py ] && { NAMES+=("99 the rotating wall: Manko-Novikov (exact rotating vacuum bumpy-Kerr; recovers Carter at q=0, none for q!=0)"); CMDS+=("scripts/99_manko_novikov_integrability.py"); }
[ -f scripts/100_emri_resonance.py ] && { NAMES+=("100 EMRI radiation reaction (GW flux validated vs Peters + frequency map; drives inspiral in Kerr & bumpy metric; bridge B1)"); CMDS+=("scripts/100_emri_resonance.py"); }
[ -f scripts/101_emri_carter_and_chaos.py ] && { NAMES+=("101 EMRI Carter flux dQ/dtau + lyapunov FD-roundoff fix (box-dim is the robust chaos detector; bridge follow-ups A + heads-up)"); CMDS+=("scripts/101_emri_carter_and_chaos.py"); }
[ -f scripts/105_chaos_frequency_drift.py ] && { NAMES+=("105 Laskar frequency-drift chaos detector (Hénon-Heiles + Kerr validated; MN thin-layer chaos exhibited on the EXACT metric — positive control closed)"); CMDS+=("scripts/105_chaos_frequency_drift.py"); }
[ -f scripts/106_zv_thin_layer_chaos.py ] && { NAMES+=("106 ZV delta=2 thin-layer chaos exhibited (layer fires + escapes, island/torus quiet — §97/§98's geometric caveat closed)"); CMDS+=("scripts/106_zv_thin_layer_chaos.py"); }
[ -f scripts/107_resonance_locking.py ] && { NAMES+=("107 resonance frequency-locking: the devil's staircase (1/5 and 1/4 plateaus in bumpy ZV; Kerr control no-lock — the quasi-static LISA signature)"); CMDS+=("scripts/107_resonance_locking.py"); }
[ -f scripts/108_dynamic_plateau.py ] && { NAMES+=("108 dynamic plateau: sustained resonance locking under drift (trapped orbit holds 1/4 while Lz sweeps; transit control sweeps past — the time-domain LISA signature)"); CMDS+=("scripts/108_dynamic_plateau.py"); }
[ -f scripts/109_integrability_lens.py ] && { NAMES+=("109 integrability/chaos as an analyzer lens (Kerr integrable · ZV delta=2 non-integrable thin-layer · specific — the toolchain, one verdict on the general tool)"); CMDS+=("scripts/109_integrability_lens.py"); }
[ -f scripts/110_two_light_rings.py ] && { NAMES+=("110 two-light-ring test (horizonless UCO has an inner STABLE ring a black hole lacks — a horizon-independent mimicker discriminator; §90 extended)"); CMDS+=("scripts/110_two_light_rings.py"); }
[ -f scripts/111_kaluza_klein.py ] && { NAMES+=("111 Kaluza-Klein reduction PROVEN (5D vacuum <=> 4D Einstein-Maxwell-dilaton, machine-derived dictionary; frozen-dilaton trap REJECTED with obstruction F^2 extracted; stacking lattice)"); CMDS+=("scripts/111_kaluza_klein.py"); }
[ -f scripts/112_kk6_two_fields.py ] && { NAMES+=("112 6D KK on T^2 (cross-coupled two-field dictionary; twist-sourcing obstruction F1.F2=0 forced by the diagonal fibre; obstruction map + consistency landscape)"); CMDS+=("scripts/112_kk6_two_fields.py"); }
[ -f scripts/113_kk6_twisted.py ] && { NAMES+=("113 6D KK TWISTED fibre (chi!=0 absorbs the F1.F2 source into its own 2nd-order EOM; §112-REJECTED two-field stacking now VERIFIED; chi = axion on SL(2,R)/SO(2), coupling F1.F2)"); CMDS+=("scripts/113_kk6_twisted.py"); }
[ -f scripts/114_flux_atlas.py ] && { NAMES+=("114 THE FLUX ATLAS (6D EM+Lambda6 on T^2: flux stabilizes VOLUME only, coset exactly flat; monodromy absorbed; geometric flux partial + compactness caveat; obstructions extracted; data/flux_atlas.json)"); CMDS+=("scripts/114_flux_atlas.py"); }
[ -f scripts/115_jacobson.py ] && { NAMES+=("115 Jacobson 1995 machine-verified (Raychaudhuri exact w/+w/o shear; area bookkeeping; Clausius constants w/ localization POSTULATE logged; lemma S(k,k)=0 => S=phi g; Bianchi => Einstein + Lambda, c=8piG)"); CMDS+=("scripts/115_jacobson.py"); }
[ -f scripts/116_cartan_karlhede.py ] && { NAMES+=("116 CARTAN-KARLHEDE decision procedure (Schwarzschild recognized across 4 charts incl. ZV delta=1 in prolate spheroidal; M=1 vs M=2 separated; type-I Kasner; VSI pp-waves DECIDED where every polynomial invariant vanishes -- the §02 blind spot closed)"); CMDS+=("scripts/116_cartan_karlhede.py"); }
[ -f scripts/117_ck_matter.py ] && { NAMES+=("117 CK matter sector (Ricci trace invariants + SEGRE type: RN derived as Segre [(11)(1,1)] electrovac, FRW fluids as [1,(111)]; flat vs radiation-universe hole CLOSED; RN recognized across Schwarzschild and Eddington-Finkelstein charts)"); CMDS+=("scripts/117_ck_matter.py"); }
[ -f scripts/118_novelty_proven.py ] && { NAMES+=("118 NOVELTY proof-backed (§02 KNOWN_LIKELY upgraded to a CK proof; FLAT_OR_VSI and BLIND_SPOT adjudicated where invariants are blind; CANDIDATE_NEW backed by a decision against every catalog entry)"); CMDS+=("scripts/118_novelty_proven.py"); }

fail=0
GATE="$(dirname "$0")/gate.log"; : > "$GATE"   # also written here so the dashboard (reads ROOT/gate.log) stays current
for i in "${!NAMES[@]}"; do
    start=$(date +%s)
    if $PY ${CMDS[$i]} >/tmp/cm_verify_$i.log 2>&1; then
        line="  PASS  ${NAMES[$i]}  ($(( $(date +%s) - start ))s)"
        echo "$line"; echo "$line" >> "$GATE"
    else
        line="  FAIL  ${NAMES[$i]}  ($(( $(date +%s) - start ))s)"
        echo "$line  — tail of log:"; echo "$line" >> "$GATE"
        tail -5 /tmp/cm_verify_$i.log | sed 's/^/        /'
        fail=1
    fi
done
echo
if [ $fail -eq 0 ]; then v="VERIFY: ALL GREEN ✅"; else v="VERIFY: FAILURES ❌"; fi
echo "$v"; { echo; echo "$v"; echo "GATE_EXIT=$fail"; } >> "$GATE"
exit $fail
