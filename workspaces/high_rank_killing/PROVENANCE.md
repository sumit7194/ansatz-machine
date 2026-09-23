# Provenance — imported from the high_rank_killing workspace

- **Source folder:** `/Users/sumit/Github/high_rank_killing` (a session working folder of the same owner, absorbed into this repo; not a separate project).
- **Copied:** 2026-09-23 23:10 IST by the ansatz-machine session, on the user's instruction. **The source was only read, never modified.**
- **Source HEAD at copy time:** `b2ebbef`; uncommitted changes in source at copy time: 7 file(s).
- **The result:** EXP-002 (`9384d7f`), EXP-003 (`6a5b66c`, WRITEUP.md added), EXP-004 (`b2ebbef`, WRITEUP amended).
- **Independent verification in this repo:** `scripts/_pp_wave_verify.py` → `data/pp_wave_verify.out`, RESULTS §147. It was run from the object alone BEFORE any of these files were read.

## ERRATUM — WRITEUP.md §7 is out of date (2026-09-23, late)
WRITEUP.md §7 says nothing was found containing the σ = 0 vacuum member. **It was published**: Filyukov,
Sci. Tech. Educ. 1(5) (2017) 13–20 (in Russian, off arXiv; INSPIRE 1620354), with its two quadratic Killing
tensors. The rank-3 tensor F = −4{Q1,Q2} was not found there. See RESULTS §147. WRITEUP.md is left
unedited as the historical record of what was believed on 2026-09-05.

## Deliberately NOT copied
- `prior_art/*.pdf`, `prior_art/*.txt` — copyrighted papers, untracked at source on purpose (commit `4397306`). Only `prior_art/README.md` (the reading list) is copied.
- `Plans/` — the sister sessions' own coordination documents; not part of EXP-002–004.
- `CLAUDE.md` is copied as `CLAUDE_original_workspace.md` so it is not auto-loaded as instructions inside this repo.
- Scripts are archived **as run**: their paths may still point at the original folder or at this repo's modules; they are the record, not a re-runnable suite.

## Source history
```
b2ebbef 2026-09-23 EXP-004: Kaluza-Klein reduction of the 5D vacuum metric verified
4397306 2026-09-05 Untrack copyrighted prior art; record the actual outcome in the README
6a5b66c 2026-09-05 EXP-003: prior art on the object (not found), CG's (2,2) cubic shown to be -1/2{Qa,Qb}, 5D Lorentzian vacuum companion; WRITEUP.md
9384d7f 2026-09-05 EXP-002: Wick-rotated CG metric is a 4D Lorentzian vacuum pp-wave with an irreducible rank-3 Killing tensor
41e1a77 2026-09-04 EXP-001: prior-art sweep — map of known higher-rank Killing tensors, TASK.md corrected
7ee6f63 2026-09-04 Workspace for the high-rank Killing tensor construction
```

## Files (sha256 of the copies)
```
ad9565ca03b6a5640d67d4eee6fd7a88b5b6331a66636b8e3c90fc8ee9f7e602  ./CLAUDE_original_workspace.md
293b508325c6ea891db20ce9acf3d676f5a2e0565493b178f7a0cdcef675dcef  ./README.md
05a27570143faf39bb77e57a47042a96f830d109a2903a990e86a4919d00ffe1  ./SISTERS.md
ac25518cb573f245d10f30d94b78ccfacb9ca1b99b96061bc73f24c7365334fc  ./TASK.md
57c8154518132932b21dbeb4b12978e04edb239b06354fd6c2cf9d2a4c32bec5  ./TODO.md
12ed1a98243469e970e598c926ca9263eb4b5857e6380512a8e233444fdd068d  ./WRITEUP.md
df2ad4960999f41dd915ced0f4ee0de2fbe9bf29e6a79a2988d1f5808f4f56b8  ./prior_art/README.md
04b5cec680f618adcc235370259792c009027a3195767fec7c576d1619754124  ./report.md
2bff49ddc76d40ac1cea8ef89caefff3b30627ad14f8655bee024fd440d62470  ./results/exp002_cg22_bracket.log
2ed5520552333bf7fc63939d3bf8b009af1f66088f65dac91581b728cb7c4fbe  ./results/exp002_cg22_relation.log
67b9b260ff985186b7029b888f6419f5796b881093c5942e0a66b65fce7a6d92  ./results/exp002_geodesic.log
8f055e444472ed139204ca20e026b94b785df6fe2ad6d37bbdf44e0352cec3c1  ./results/exp002_jac_noQ2.log
5b99a6676627b3b326dd67b1ab32c4f611575cb702818a3449ead1e20e063eff  ./results/exp002_relation.log
ebe154e6cb21db679ae92d33194540b59c824d79717fed9dd32faa8ab8a44957  ./results/exp002_sibling_prover.log
2d34b338014aa76611c11bbde14c08693a6b3dcdded8321d2794b55d928cc5c5  ./results/exp002_tier1.log
7162debf1478c9bd7f6bfc20f55712997f1bc16d63d1dd7ba8595f053fb90c32  ./results/exp002_tower.log
5648589ba394d0b6fb806718f866a9427bcf1e81ad22b21e3b59e94eaf06989e  ./results/exp003_5d.log
edbf1ade8f8a5570049c15f7aa0d8f981879383451988eed302862d364971621  ./results/exp003_5d_squeeze.log
8467d32ac7ddbce02c90a62f9320164f752f724b9de34a503881121dc7b5bd93  ./results/exp004_4d_em_kt.log
bf1e3e11be0039a900eae78b4ecc5d60ca6965ab0df3e0b34983a4b4cbdce807  ./results/exp004_kk.log
9249437e14c16552c6f779ae22b432105bbef663812a0b57c5c8ba86aff53459  ./results/exp004_kk_firstrun.log
4fff0e51b0430acc8a270a7b756b108cbe10d325b8c5d1c21769b0ce25ac34d8  ./scripts/exp002_cg22_bracket.py
18646ba9d7bca9fd58ec04bad0638f35dd9c2063ca4baa61e6f439213c7651ca  ./scripts/exp002_cg22_relation.py
b5e3f1d4efcbb0d94cb80f22d7da0f07a7398314ad949ab7aab41970c010b35f  ./scripts/exp002_geodesic_check.py
91485065ae3545bf354f5979eea188ae739ddaecc9dc326dc2d4340645cda957  ./scripts/exp002_jac_noQ2.py
5c519926283a41601eb1f44e38e1e68a78bfb1e07ab9f0c6380319b753732838  ./scripts/exp002_ppwave.py
1b066399544a59bf8e65798b80cc1456fe118b701e388c30c80b9b0653ca2bb4  ./scripts/exp002_relation_check.py
5c82204241c7d4c531f3775e3f4d21b293454c4b5e487b1713fa8ff23cb8b95e  ./scripts/exp002_sibling_prover.py
0d33f6166873d299a9e63c8921e8bb938c84094fcc21c24ac8b9942012323c84  ./scripts/exp002_tower.py
b81c3e7334d710b30272bbb5d719d8963a17893a425099b31850137134291fac  ./scripts/exp003_5d_gyraton.py
8fe08367a009756ed6d8b7db17e0c5969ab10b72e59065249db967947bd3eb18  ./scripts/exp003_5d_squeeze.py
99d0dabcb9298c9630d5247b90b8dec48dc249a55fb99705fcfdff9c2b9e58cc  ./scripts/exp004_4d_em_kt.py
d8d7b4d9d783d97fa1bc99ad8b713c45d959ed6c6046f8950beeb77d1343bc4b  ./scripts/exp004_kk_reduction.py
```
