# SP package: status, diagnosis and resubmissions, 28 October 2026

What a direct survey of `hpc1:~/system_development/05_qmmm/24_sp_barriers` and of PBS job history
shows, what is running, and what was resubmitted today. Measured, not taken from any report.
`HANDOVER_20261026.md` §4's snapshot is superseded by this.

This note changes no pre-registration. `SP_PLAN.txt`, `SP_AMENDMENT1.txt`, `SP_AMENDMENT2.txt`,
`SP_AMENDMENT3.txt` and the errata are untouched.

---

## 1. How a frame is counted

A frame is COMPLETE when all nine protocol stages — `ts`, `ts_freq`, `irc`, `r_irc`, `r_irc_freq`,
`p_irc`, `p_irc_freq`, `r0`, `r0_freq` — hold outputs and every run in them terminated normally.

The alternation stages (`ts`, `r_irc`, `p_irc`, `r0`) keep their outputs in `cNN_core` / `cNN_env`
cycle subdirectories, one level below the stage directory (`SP_AMENDMENT1`'s alternating scheme).
**A non-recursive file count therefore reports those stages as empty and makes it appear that no
frame has a complete chain.** Any audit of this package must recurse.

## 2. The number

| | frames |
|---|---|
| **COMPLETE** | **15** |
| **`SP_AMENDMENT2` A2.3 floor** | **20** |
| unfinished, no fault, work already queued | 9 |
| r0 branch lost to a node failure — resubmitted today | 6 |
| carrying a genuine fault | 4 |

COMPLETE: 21634 23268 24883 26495 33320 40485 41786 42436 45688 46990 47641 48292 49592 52192 59999

Across all 36 directories: **1,947 ORCA outputs, 1,721 terminated normally**, 36 GB on hpc1.
Of the 15 complete frames, only `f42436_r8_a1` has been harvested into this repository (x77 batch 2).

## 3. Why six frames lost their entire r0 branch

| job | frame | dispatched | ended | alive | exec_host | Exit_status | run_count |
|---|---|---|---|---|---|---|---|
| 420763 | f53493 | 16:17 | 16:19:25 | 145 s | comp036.hpc/0*16 | **−2** | 1 |
| 420771 | f54144 | 16:19 | 16:21:07 | 127 s | comp036.hpc/0*16 | **−2** | 1 |
| 420779 | f54795 | 16:21 | 16:22:48 | 108 s | comp036.hpc/0*16 | **−2** | 1 |
| 420787 | f55446 | 16:22 | 16:24:25 | 145 s | comp036.hpc/0*16 | **−2** | 1 |
| 420795 | f56098 | 16:24 | 16:26:01 | 121 s | comp036.hpc/0*16 | **−2** | 1 |
| 420803 | f57397 | 16:26 | 16:27:37 | 97 s | comp036.hpc/0*16 | **−2** | 1 |

All six on **one node**, on **22 October 2026 within ten minutes**. Each was dispatched with its
full 16 cores and 64 GB, failed to execute after about two minutes having used no CPU time, and PBS
did not retry. A negative `Exit_status` is PBS's own, not the job script's; `−2` is the no-retry
variant, which is why no `job_r0.pbs.out` was ever written for any of them.

**Control.** Job 420781, `f55446`'s `ts`, from the same submission block at the same time, landed on
**comp045** and returned `Exit_status = 0`.

`job_r0` is the only job in the chain with no predecessor (`x84_pkg_waves.py` `PRED`), so those six
were the ones eligible and at the front of the queue whenever comp036 came free. That is why this
branch and no other was hit.

**Hypotheses this disproves**, each entertained and discarded during the diagnosis: memory
exhaustion; the 176-hour walltime against the queue maximum (`week` allows exactly 176:00:00);
`afterok` propagation from an upstream failure; a queue-time purge of long-queued jobs; and a
systematically marginal alternation cycle cap.

## 4. Resubmitted, 28 October 2026

| frame | `job_r0` | `job_r0_freq` |
|---|---|---|
| f55446 | 422557 | 422558 |
| f53493 | 422559 | 422560 |
| f54144 | 422561 | 422562 |
| f54795 | 422563 | 422564 |
| f56098 | 422565 | 422566 |
| f57397 | 422567 | 422568 |

Submitted exactly as `submit.sh` does it — `job_r0.pbs` with no dependency, then `job_r0_freq.pbs`
with `-W depend=afterok:<r0>`. Each folder's `SUBMITTED` was copied to `~/sp_resubmit_20261028/`
and then had its `job_r0` and `job_r0_freq` ids replaced in place: `x84_pkg_waves.py` reads that
file and stops on a ninth line or an unexpected one, so it must stay at exactly eight.

**These six landing takes the package from 15 complete to 21, past the floor of 20.** Everything
else those frames need is already queued or already done; f55446 needed nothing but this pair.

## 5. What is running

29 jobs across 12 frames, all generation 2, all queued on
`comment = Not Running: Insufficient amount of resource: mem`. Not walltime. The queue held 98
running at the time of the survey. Disk and quota are not constraints: 8,530 GB free on the
filesystem, 861.8 GB of quota left against 114.8 GB used, and no per-user limits on queued work.

## 6. The four genuine faults

| frame | fault |
|---|---|
| **f34991** | `r0` ran 65 h 43 m of a 176 h allowance and hit the **20-cycle cap** while still descending — 0.0497, 0.0379, 0.0320 kcal/mol over cycles 18–20 — giving `SP_r0_FAIL`, so `afterok` deleted `r0_freq`. Not a crash. Raising the cap would be a change to `SP_AMENDMENT1`'s alternating scheme and needs a dated amendment. |
| **f44388** | `r0` failed at **cycle 2**. A different fault, undiagnosed. |
| **f36665** | `irc` died mid-iteration at step 10 with no termination; its four dependents were purged by `afterok`. |
| **f20000** | `ts` failed 11/12, and it is the only folder still on generation 1. Its `ts/` holds 11 normally-terminated outputs but no `job_ts.pbs.out`, which is unexplained. |

**The cycle cap is not marginal.** Across 29 frames: `ts` 4–14 (median 8), `r_irc` 3–9 (6),
`p_irc` 3–11 (5), `r0` 2–20 (6). Outside f34991's `r0` the highest any stage reaches is 16, and
every other `r0` is at or below 12. f34991 is an outlier, so this is one frame to rerun and not a
protocol problem.

## 7. Three submission generations, and a provenance gap

| first job id | folders | |
|---|---|---|
| 418271, 418279 | f42436_r8_a1, f42436_r6_a1 | earliest, outside the package |
| 419762, 419770 | f20000_r8_a1, f20000_r8_ci_a1 | generation 1, 19 Oct — **never resubmitted** |
| 420597 … 420836 | the other 30 folders | generation 2, submitted **21 Oct 12:39** |

Generation-2 ids step by exactly 8 per folder: one contiguous submission of 240 jobs.

**There is no log for generation 2.** `package_waves/` holds only `wave_1.txt` (19 Oct 14:32) and
`staging/` only `x84_submit_20261019_143037.log`. `x84_pkg_waves.py` reads job ids from each
folder's `SUBMITTED`, which carries generation 2, so its per-job states are sound — but its "waves
so far: wave 1" is stale, and `HANDOVER_20261026.md` §4's "90 job lines at 09:58, 26 October" was a
snapshot of generation 2 in flight, not a submission event.

## 8. Harvest — not done, and what it requires

`x77_sp.sh` (results `00_admin/hpc_cleanup_smoke1/batch_2/scripts/`) is the tool for this, and
`X77_SP_OUTPUTS_20261018.md` already records the outstanding work: *"x77 covers only these four
runs: the package runs need it extended to their folders before their outputs are collected."*

It implements the standing rule of 18 October — every output downloaded to a PC archive **and**
the text subset committed, not merely reported. `hpc_text_outputs_2_*` is **batch 2**, so the
package frames would be batch 3 onward.

Sizing, scaled from the one committed frame (`f42436_r6_a1`: 227.1 MB of raw `.out` + `.hess` →
87 MB committed):

- 14 complete-but-unharvested frames ≈ **1.23 GB** of git payload;
- x77 stops a batch above **1.5 GB** and cannot split one, so 18 % headroom on a single-frame
  extrapolation is thin — two batches of seven (≈ 660 MB and ≈ 600 MB) is the safer shape;
- the PC archive side is roughly **16 GB** of files on hpc1 for those frames [estimate].

Deferred by decision on 28 October: harvest once the queued work lands, rather than committing
partial frames now.

## 9. Open

- Whether comp036 was drained after 22 October, and why the failures returned the no-retry `−2`
  rather than `−3`, which would have requeued them automatically.
- f44388's `r0` failing at cycle 2.
- f20000 stranded on generation 1, and its missing `job_ts.pbs.out`.
- Whether any other generation-2 job was caught by comp036 in that window.
- f34991's cap: rerun with more cycles under a dated amendment, or accept the frame as it is.
