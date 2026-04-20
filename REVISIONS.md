# pool_path — Revision Log

A running record of the refactor work done on this project. Each entry covers **what changed, why, the actual before/after, and the concrete benefit.**

The overall goal is to make this codebase easier to read, faster to run experiments on, and easier to visualize results from. Work is staged in three phases:

- **Phase 1 — Readability** (done, 4 of planned 5 tasks complete; `np.matrix → np.array` deferred)
- **Phase 2 — Scalability** (in progress; 3 of 6 done)
- **Phase 3 — Visualization** (not started)

---

## Prerequisite: environment fixes

Before any refactor, the project wouldn't run on the current machine (Python 3.14, NumPy 2.4). These were forced fixes, not revisions — listed here for completeness.

| Issue | Fix |
| --- | --- |
| `ModuleNotFoundError: gltf` | `pip install panda3d-gltf` (the correct Panda3D GLB loader) |
| `ModuleNotFoundError: simplepbr` | `pip install panda3d-simplepbr` |
| `ModuleNotFoundError: scipy` | `pip install scipy` |
| `TypeError: only 0-dimensional arrays can be converted to Python scalars` | `float(tballs[i].pos[0])` → `tballs[i].pos[0].item()` (NumPy 2.x no longer auto-converts 2D `np.matrix`) |
| `AttributeError: 'NoneType' object has no attribute 'set_minfilter'` | Added `findAllTextures()` fallback in `pooltool/objects/ball/render.py` — GLB embedded textures have empty names, so `find_texture("cue")` returned None |
| `Exception: Attempt to spawn multiple ShowBase instances!` | Made `_interface` a module-level singleton in `test_control.py` (created once, reused) |
| `SyntaxWarning: invalid escape sequence '\e'` | Path literal `"allheatmap\eval_interpolated/..."` → `Path("allheatmap") / "eval_interpolated" / ...` |
| `import gltf` side-effect missing | Added `import gltf  # registers Panda3D GLB/GLTF loaders` to `pooltool/ani/animate.py` |

---

## Phase 1 — Readability

### Revision 1.1 — Remove dead code in `main_with_simulator.py`

**What:** Deleted ~120 lines of commented-out Case 1–9 ball layouts inside `'''...'''` blocks, removed unused imports (`MouseButton`, `tkinter`, `algo`, `math`, `Graphic`), removed orphan function `draw_without_after_track`, removed unused `color` list.

**Why:** The file was 439 lines; the majority was commented-out code from prior experiments that made the actual logic hard to find. Comments-as-code is also a maintenance trap — someone eventually "fixes" dead code and ships bugs.

**Diff (size):** `main_with_simulator.py` 439 → 181 lines (**−59%**).

**Benefit:** The entry point is now readable top-to-bottom. Nothing in the file is ambiguously "is this live?"

---

### Revision 1.2 — Cross-platform path for heatmap load

**What:** Replaced Windows-style string path with `pathlib.Path`.

**Why:** `"allheatmap\eval_interpolated/reshape_60_100.npy"` triggered `SyntaxWarning: invalid escape sequence '\e'` and silently failed on macOS/Linux because `\e` was interpreted as an escape character by Python's string parser. Using `Path` makes it platform-neutral and warning-free.

**Diff:**
```diff
- heatmap = np.load("allheatmap\eval_interpolated/reshape_60_100.npy")
+ heatmap = np.load(Path("allheatmap") / "eval_interpolated" / "reshape_60_100.npy")
```

**Benefit:** Script runs on macOS/Linux without warnings; path segments are OS-native on Windows too.

---

### Revision 1.3 — Rename ambiguous identifiers

**What:** Renamed identifiers throughout `main_with_simulator.py` to match their actual meaning.

**Why:** Names like `Dis`/`Ang`/`returnD`/`returnE` gave no hint what they were — `Dis` was spin magnitude, `Ang` was spin angle in degrees, `returnD/E` echoed those back from `simulate()`. Reading the code required cross-referencing `test_control.py:simulate()` just to remember what each variable was. Good names remove that tax.

**Key renames:**

| Before | After | Meaning |
| --- | --- | --- |
| `Dis`, `D` | `spin_mag` | Cue tip offset magnitude (spin intensity) |
| `Ang`, `E` | `spin_ang` | Cue tip offset angle in degrees |
| `returnx`, `returny`, `returnangle`, `returnD`, `returnE`, `returnspeed` | `res_x`, `res_y`, `res_angle`, `res_spin_mag`, `res_spin_ang`, `res_speed` | Shot-result tuple from `simulate()` |
| `CueFinalPos`, `Cuefianlposition` | `cue_final_positions` | List of candidate cue-ball final positions |
| `bestone` | `scored_positions` | Positions with heatmap scores attached |
| `testinfo` | enumerate index | Loop variable in scoring loop |
| `temp` | `score` | Heatmap lookup result |

**Benefit:** You can read `record_shot(angle, spin_mag, spin_ang, speed)` and know what's being swept, without opening another file.

---

### Revision 1.4 — Collapse the 9-branch `if/elif` in `test_control.py`

**What:** Rewrote `test_control.py` from 177 → 116 lines. Replaced nine near-identical `if n == 1: ... elif n == 2: ...` branches (each constructing `pt.System(...)` with a slightly different ball dict) with a single `_build_target_balls()` helper plus one clean `simulate()` function.

**Why:** The original dispatched on the number of target balls, duplicating the entire `pt.System` + `shot.strike` code block nine times. Any fix to shot physics required nine edits — an invitation to skew. The pattern underneath is simple: for `n` targets, ball IDs are `[9−n+1 … 9]`, with two quirks worth preserving.

**The two preserved quirks (now explicit, not hidden in branches):**
1. **`n=9` skips balls "4" and "8"** — matches the original paper's 9-ball setup (balls 1, 2, 3, 5, 6, 7, 9).
2. **`n=8` uses a `+3` cut offset** where all other `n` use `-3` — preserved verbatim with an explanatory comment.

**Diff shape:**
```diff
- if n == 1:
-     shot = pt.System(... balls={"cue": ..., "9": ...})
-     shot.strike(phi=pt.aim.at_ball(shot, "9", cut=-cutangle - 3))
- elif n == 2:
-     shot = pt.System(... balls={"cue": ..., "8": ..., "9": ...})
-     shot.strike(phi=pt.aim.at_ball(shot, "8", cut=-cutangle - 3))
- elif n == 3:
-     ... (7 more near-identical branches)

+ balls = {"cue": pt.Ball.create("cue", xy=[Cuex, Cuey], ballset=ballset)}
+ balls.update(_build_target_balls(Target, ballset))
+ shot = pt.System(table=..., cue=..., balls=balls)
+
+ aim_target_id = "1" if n == 9 else str(9 - n + 1)
+ cut_offset = 3 if n == 8 else -3
+ shot.strike(phi=pt.aim.at_ball(shot, aim_target_id, cut=-cutangle + cut_offset))
```

**Benefit:** One code path for shot construction. The quirks are now visible as named conditions rather than buried in branch N. Adding a new target count takes zero code changes.

---

### Revision 1.5 — *deferred*: `np.matrix` → `np.array`

**Why deferred:** `np.matrix` is deprecated in NumPy, but the rewrite is risky — `*` on `np.matrix` means matrix-multiply, while on `np.array` it's element-wise. `algo.py:43–47` mixes scalar-by-matrix `*` with matrix-by-matrix `*` in the same expression. A silent mistranslation produces wrong shot geometry with no traceback. This is planned as the final Phase 1 task, after Phase 2 establishes verifiable headless runs (so a before/after diff of shot outputs becomes possible).

---

## Phase 2 — Scalability

### Revision 2.1 — Decouple `ShotViewer` from `simulate()`

**What:** Added `visualize=False` parameter to `simulate()` in `test_control.py`. The 3D window only opens when explicitly requested.

**Why:** `pt.ShotViewer.show()` calls Panda3D's `task_mgr.run()` internally — it **blocks until the user manually closes the window.** The sweep in `main_with_simulator.py` makes **384 simulate calls per scenario**. That meant closing 384 windows by hand to finish one run. In practice the script was never completing — the scatter plot PNG never saved because earlier runs got cut short.

**Diff:**
```diff
- def simulate(Cuex, Cuey, Target, cutangle, D, E, speed):
+ def simulate(Cuex, Cuey, Target, cutangle, D, E, speed, visualize=False):
      ...
      pt.simulate(shot, continuous=True, inplace=True)
-     if _interface is None:
-         _interface = pt.ShotViewer()
-     _interface.show(shot)
+     if visualize:
+         if _interface is None:
+             _interface = pt.ShotViewer()
+         _interface.show(shot)
```

**Benefit:** The full sweep runs headless to completion in seconds rather than stalling forever. Interactive debugging still works — pass `visualize=True` to any single call. This is the single most important unblocking change in the project.

---

### Revision 2.2 — Collapse triple-nested sweep with `itertools.product`

**What:** Replaced a 28-line triple-nested `while` pyramid plus 3 hand-written baseline calls with a `record_shot()` local helper and an `itertools.product` grid.

**Why:** The sweep was hard to read and had a latent bug. The speed increment was:
```python
if spin_mag < 0.3:
    speed += 1.5
else:
    speed += 0.5
```
But this ran **after** the inner loop exited, at which point `spin_mag` had already overflowed past 0.6. The `< 0.3` branch was dead. Effective step was always `+0.5`. The explicit grid now reflects what actually runs.

**Diff (structural):**
```diff
- res_x, res_y, ... = tc.simulate(..., -13.21, 0, 0, 1)
- cue_final_positions.append([round(res_x, 4), ..., res_speed])
- print('simulate', len(cue_final_positions), 'times\r', end=' ')
- (...two more copy-pasted baseline calls...)
- speed = 1
- while speed <= 2.5:
-     spin_mag = 0.05
-     while spin_mag <= 0.6:
-         spin_ang = 0
-         while spin_ang <= 315:
-             res_x, res_y, ... = tc.simulate(..., angle, spin_mag, spin_ang, speed)
-             cue_final_positions.append([...])
-             print('simulate', ...)
-             spin_ang += 45
-         spin_mag += 0.05
-     if spin_mag < 0.3:
-         speed += 1.5
-     else:
-         speed += 0.5

+ def record_shot(cutangle, spin_mag, spin_ang, speed):
+     res = tc.simulate(p1x/100, p1y/100, tball_simple_pos, cutangle, spin_mag, spin_ang, speed)
+     ...
+     cue_final_positions.append([...])
+
+ record_shot(-13.21, 0, 0, 1)
+ record_shot(angle, 0, 0, 2.5)
+ record_shot(angle, 0, 0, 2)
+
+ speeds = [1.0, 1.5, 2.0, 2.5]
+ spin_mags = [round(0.05 * i, 2) for i in range(1, 13)]  # 0.05 .. 0.60
+ spin_angs = list(range(0, 316, 45))                     # 0, 45, .., 315
+
+ for speed, spin_mag, spin_ang in product(speeds, spin_mags, spin_angs):
+     record_shot(angle, spin_mag, spin_ang, speed)
```

**Shot count:** 3 baseline + 4 × 12 × 8 = **387 shots** (same as before; dead branch preserved as the original effective behavior).

**Benefit:** The parameter grid is now a single named variable. Want finer spin resolution? Change one list literal. Want to add cut-angle sweeps? Add one list and one `product` dimension. The intent is self-evident.

---

### Revision 2.3 — Externalize scenario to YAML

**What:** Moved the hardcoded 9-ball layout out of `main_with_simulator.py` into `scenarios/9ball.yaml`. Added a `load_scenario()` function.

**Why:** The layout was 12 lines of inline Python literals. Swapping to a different ball arrangement meant editing source and committing, which discouraged running variations. A data file is lower-friction to create, compare, and share (e.g. attach to a paper).

**Diff:**

New file `scenarios/9ball.yaml`:
```yaml
name: 9ball
cue: [43.5, 95.75]
targets:
  - [47.1, 113.8]   # ball 1
  - [81.5, 176.0]   # ball 2
  - [48.5, 162.0]   # ball 3
  - [44.0, 155.0]   # ball 4
  - [65.5, 158.0]   # ball 5
  - [29.75, 38.5]   # ball 6
  - [27.0, 124.25]  # ball 7
  - [4.0, 159.0]    # ball 8
  - [64.0, 94.0]    # ball 9
```

In `main_with_simulator.py`:
```diff
- # 9-ball layout — (x, y) in cm on a 104x208 table
- cue_pos = (43.5, 95.75)
- target_positions = [
-     (47.1, 113.8),   # ball 1
-     (81.5, 176),     # ball 2
-     ... (7 more lines)
- ]

+ def load_scenario(path):
+     with open(path) as f:
+         data = yaml.safe_load(f)
+     return data["cue"], data["targets"]
+
+ scenario_path = Path("scenarios") / "9ball.yaml"
+ cue_pos, target_positions = load_scenario(scenario_path)
```

**Benefit:** New scenarios are new `.yaml` files. No Python edits, no risk of accidentally commenting out the wrong block. Sets up Revision 2.4 (CLI), where the scenario becomes a flag.

---

### Revision 2.4 — CLI via `argparse`

**What:** Wrapped the top-level script body in a `main()` function behind an `if __name__ == "__main__":` guard, parsed three flags with `argparse`, and threaded them through to the right places:

- `--scenario PATH` (default `scenarios/9ball.yaml`) — which YAML layout to load.
- `--visualize` — if set, opens the 3D `ShotViewer` for every shot (blocks per shot; for debugging).
- `--output-dir PATH` (default `.`) — where to write the scatter PNG.

Also extended `pool()` and `load_scenario()`:
- `pool(..., visualize=False)` — forwards the flag down to `record_shot()` → `tc.simulate(..., visualize=...)`.
- `load_scenario()` now returns the full YAML dict so `main()` can read the scenario `name` and use it in the output filename (`scatter_{name}.png`).

**Why:** Previously, changing scenario, toggling visualization, or redirecting output all required editing source. That made experiments painful to script and impossible to reproduce from a command history. With a CLI:

- `./venv/bin/python main_with_simulator.py --scenario scenarios/9ball.yaml`
- `./venv/bin/python main_with_simulator.py --visualize` (debug one shot)
- `for s in scenarios/*.yaml; do ./venv/bin/python main_with_simulator.py --scenario "$s" --output-dir "results/$(basename $s .yaml)"; done`

The command itself becomes the reproducibility record.

**Diff (structural):**
```diff
+ import argparse
  ...
- def pool(mball, tballs, cushion_amt, path_amt):
+ def pool(mball, tballs, cushion_amt, path_amt, visualize=False):
  ...
-         res = tc.simulate(..., speed)
+         res = tc.simulate(..., speed, visualize=visualize)
  ...
- start_time = time.time()
- ... (45 lines of module-level setup/load/sweep/plot) ...
- plt.savefig('scatter_9ball.png', dpi=600)

+ def load_scenario(path):
+     with open(path) as f:
+         return yaml.safe_load(f)
+
+ def parse_args():
+     p = argparse.ArgumentParser(...)
+     p.add_argument("--scenario", type=Path, default=Path("scenarios") / "9ball.yaml")
+     p.add_argument("--visualize", action="store_true")
+     p.add_argument("--output-dir", type=Path, default=Path("."))
+     return p.parse_args()
+
+ def main():
+     args = parse_args()
+     start_time = time.time()
+     scenario = load_scenario(args.scenario)
+     name = scenario.get("name", args.scenario.stem)
+     ...
+     cue_final_positions = pool(mball, tballs, 4, 1, visualize=args.visualize)
+     ...
+     args.output_dir.mkdir(parents=True, exist_ok=True)
+     scatter_path = args.output_dir / f"scatter_{name}.png"
+     plt.savefig(scatter_path, dpi=600)
+
+ if __name__ == "__main__":
+     main()
```

**Verification:** `python main_with_simulator.py --help` now lists all three flags; the output filename derives from the scenario's `name` field (or falls back to the YAML stem).

**Scope note — intentionally left out:** I did not add a `--top-k` flag. The existing top-K print loop (`range(11, len(...)+1)`) has semantics that conflict with its comment ("top-10 highest-scoring") — it actually **skips** the top 10 and prints everything below. Parameterizing it would either preserve a confusing behavior or silently change output. That's a separate logic fix; keeping the CLI refactor clean.

**Benefit:** Experiments are now shell-scriptable. Adding new scenarios doesn't require touching the script. Each run's output is isolated to its own directory. `--help` documents every knob.

---

### Revision 2.5 — Persist results as CSV

**What:** Every run now writes `results_{name}.csv` into `--output-dir`, one row per simulated shot, with a proper header.

**Columns:** `shot, x, y, cut_angle, spin_mag, spin_ang, speed, score`

- `shot` — 0-indexed shot number (matches the order of the sweep).
- `x, y` — cue-ball final position in table units (meters from table corner).
- `cut_angle, spin_mag, spin_ang, speed` — input parameters for that shot.
- `score` — heatmap lookup value at `(x, y)`.

**Why:** Before this, the only artifact from a run was a PNG scatter — no numeric output, no way to diff two runs, no way to re-plot without re-running all 387 shots. CSV is the smallest viable format: opens in Excel, pandas, R, or `grep`. It also makes regression testing trivial for the deferred `np.matrix → np.array` refactor — run once before, once after, `diff` the CSVs.

**Diff:**
```diff
+ import csv
  ...
+ # dump per-shot results to CSV: one row per simulated shot, including heatmap score.
+ csv_path = args.output_dir / f"results_{name}.csv"
+ score_by_index = {i: s for i, s in scored_positions}
+ with open(csv_path, "w", newline="") as f:
+     writer = csv.writer(f)
+     writer.writerow(["shot", "x", "y", "cut_angle", "spin_mag", "spin_ang", "speed", "score"])
+     for i, pos in enumerate(cue_final_positions):
+         writer.writerow([i, *pos, score_by_index[i]])
```

Uses only the standard library (`csv` module) — no new dependency.

**Benefit:**
- **Post-hoc analysis.** Load in pandas once, slice the top-K by score, group by `speed`, plot spin-angle sensitivity — none of which requires re-running the simulation.
- **Reproducibility.** The CSV + the exact CLI command is a complete record of an experiment.
- **Regression-testable.** Two CSVs from equivalent commands should match byte-for-byte (or diff cleanly); a silent physics regression becomes immediately visible.
- **Interoperable.** Can be consumed by any downstream tool — the project stops being a closed loop of Python-only code.

---

### Revision 2.6 — Fix silent `path_dict` overwrite

**What:** Replaced a `dict` keyed by evaluation score with a list of `(evaluation, node)` tuples, then sorted by score using an explicit key function.

**Why:** The original code built `path_dict[evaluation] = path_node` inside a loop. Python dicts enforce unique keys — so if two different candidate paths scored identically (same float `evaluation`), the second one **silently overwrote** the first. Result: paths vanished from the final ranking with no warning. For a search that's supposed to enumerate and rank candidates, losing any of them is a correctness bug.

Since `evaluation` is a float produced by summing distances, ties are rare but possible, and certainly possible near integer grid positions. The bug mode was: you'd never know how many paths you actually lost, and a "better" path might be silently replaced by a slightly worse one with the same score.

**Diff:**
```diff
  path_node = avail_paths.first
- path_dict = {}
- while path_node != None:
+ scored_paths = []
+ while path_node is not None:
      moving_list = path_node.moving_list
      evaluation = path.calculate_evaluation(moving_list)
-     path_dict[evaluation] = path_node
+     scored_paths.append((evaluation, path_node))
      path_node = path_node.next

- sorted_paths = sorted(path_dict.items())
+ sorted_paths = sorted(scored_paths, key=lambda item: item[0])
```

The explicit `key=lambda item: item[0]` matters: with a list of tuples, if two items tie on `evaluation`, Python's sort would otherwise try to compare the second elements (PathNode objects) to break the tie — and PathNode has no `__lt__`, which would raise `TypeError`. The key lambda sidesteps that by comparing only evaluations.

Downstream access (`sorted_paths[i][0]` for score, `sorted_paths[i][1]` for node) is unchanged, so this is a drop-in fix.

**Benefit:**
- No silent path loss. The ranking now contains every candidate.
- Ties are preserved in the order they were discovered (Python's `sort` is stable).
- Also a small idiomatic win: `path_node is not None` replaces `path_node != None` (the former is the correct way to compare to `None` — `!=` can be overridden by a class's `__ne__`; `is` can't).

---

## Phase 2 — complete

All six Phase-2 scalability revisions are done. The project now:
- Runs headless (no per-shot window blocking).
- Has a clean parameter grid you can edit in one place.
- Loads scenarios from YAML files.
- Exposes a CLI with `--scenario`, `--visualize`, `--output-dir`.
- Writes numeric results to CSV per run, alongside the scatter PNG.
- Preserves every candidate path through the scoring/sort step.

A full sweep run from the command line:
```bash
./venv/bin/python main_with_simulator.py --scenario scenarios/9ball.yaml --output-dir results/exp_01
# produces:
#   results/exp_01/results_9ball.csv
#   results/exp_01/scatter_9ball.png
```

## Phase 3 — not started

Heatmap overlay on scatter; trajectory polylines; mirror-table tree visualization; `logging` instead of `print`; per-scenario report directory.

---

## Summary of benefits so far

| Dimension | Before | After |
| --- | --- | --- |
| Entry point size | 439 lines | 181 lines |
| Shot construction | 9 duplicated branches | 1 helper |
| Sweep loop | 28 lines, buggy step logic | 10 lines, explicit grid |
| Full-scenario run time | Never completes (384 blocking windows) | Runs headless |
| Scenario change | Edit + commit Python | Edit YAML |
| Script on a fresh Python 3.14 machine | 7 different errors | Runs |
