# Jobs still running at the time of this commit

Recorded 2026-09-30. **Every ensemble number in this repository is provisional
until these finish.** When they do, run `harvest`, then `sweep.sh`, then the
in vacuo batch, and update the figures listed at the bottom.

## Still in the queue

| job id | name | frame | elapsed at commit | note |
|---|---|---|---|---|
| 412717.hpc1.hpc | cm19_n443* | 44388 | 43h36m | **Beyond every completed run.** The longest that has finished is 42436 at 22h41m. No basis to estimate a remaining time. If `neb.out` stops growing for more than an hour it has stalled and should be killed; the 176 h walltime will not free the slot until 6 October. |
| 413741.hpc1.hpc | cm19_n599* | 59999 | 18h14m | Above the 7.2 h mean but within the observed range. |
| 413447.hpc1.hpc | cm19_x476* | 47641, 16-image rerun | 20h59m | Not part of the ensemble. A resolution check: frame 47641 rerun with `NImages 16` instead of 8. Writes to `05_qmmm/nimg_test/frame_47641`, job name `cm19_x` so the runner cannot confuse it with the real frame. |

## What is provisional

- **28 of 30** new frames have converged. 44388 and 59999 are outstanding.
- **41 frames carry a barrier**; **35 have `stab_TS`**. Six converged frames
  still need their in vacuo single points: **54144, 54795, 55446, 56098, 57397,
  58698**. Run `s8_invacuo_new.pbs` with those in `export FRAMES` on line 46.

## Figures that will move

Every one of these is quoted in commit `adf226b` and in the two decision notes,
and every one is computed from the 28 or 35 frames available on 30 September:

- 28 new-frame barriers: mean 13.44 +/- 4.42, sem 0.84, median 14.43,
  range 3.41 to 19.29
- 35 frames with both quantities: barrier 13.60 +/- 4.99, in vacuo
  18.44 +/- 2.25, stab_TS -4.85 +/- 4.33
- barrier-on-stabilisation regression: gradient 1.029, intercept 18.58,
  r +0.893

The projection from the validated guess-height predictor
(`barrier = 0.837 * dE/win01 + 0.57`, mean absolute residual 0.57 kcal/mol over
19 out-of-sample frames) puts the final 30-frame mean at about **13.4 +/- 0.8**,
so the two outstanding frames are expected to move the mean by roughly 0.2 -
less than the standard error. The regression gradient and correlation cannot be
projected and must be recomputed.

## The 16-image test

At the time of commit it had completed 4 LBFGS iterations without converging.
The comparison against the 8-image run is already decisive and is recorded in
HANDOFF.md section 6: highest-energy image at fractional path position 0.647
against 0.667, energies agreeing to 0.037 kcal/mol at every matched iteration.
A converged second point would strengthen that from four iterations of agreement
to a converged comparison, but it does not change the conclusion.
