# Terminology

[<- back to the main README](../README.md)

This file names the words this project uses for the search, one per concept.

This file binds prose and identifiers alike.
It covers the docstrings, the comments, the error messages,
every document under `docs/` and the README,
and the names of classes, methods and arguments.

Every word that is not about the search,
such as task, worker, pilot job, job group, queue, driver and executor,
comes from
[the `slurm-workflows` terminology](https://github.com/parantapa/slurm-hpc-workflows/blob/main/docs/terminology.md).
That file also says where its words come from:
Slurm first, then `ds-service`, then the library's own API.
Use its words here, with the same sense and the same spelling.

## The four rules

These are the rules of the `slurm-workflows` terminology,
repeated here because the search section leans on them.

1. **Bare "task" means a `ds-service` task.**
    Every other sense is qualified, every time.
2. **The driver is a process.
    The executor is an object.**
    If a sentence stays true with two executors in one program,
    it is about the driver.
3. **A worker is a process.
    A pilot job is a Slurm job.
    A job group is a group of pilot jobs.**
4. **One name per thing.**
    Where a paragraph wants a second word for variety, it does without.

## The search side

Neither Slurm nor `ds-service` has a word here.
These words come from this library's own API,
from botorch where the code calls into it,
and from scipy for the design.

| Term | What it names | Source | Do not use |
| --- | --- | --- | --- |
| **study** | One space, its objective and its settings. | Optuna | task, job, problem, experiment |
| **exploration** | What `ExploreSpaceSobolQMC` does. | `num_exploration_points` | sweep, sampling, scan |
| **search** | What `OptimizeSpaceBotorch` does. | `search_parallelism` | optimization as the activity, calibration, tuning |
| **round** | One fit-propose-evaluate cycle. | this library | iteration, phase, wave, generation |
| **design** | The set of points a Sobol' draw produces. | scipy qmc | sample, batch, grid |
| **point** | A parameter assignment, in objective coordinates. | this library | sample, config, trial |
| **unit point** | The same point in the unit cube. | `unit_points` | standardized point, normalized point |
| **candidate** | A point the acquisition proposed and nothing evaluated yet. | botorch | proposal as a noun, suggestion |
| **observation** | An evaluated point, with its value. | botorch, GP literature | result, measurement, data point |
| **objective** | The function under study. | this library | target, cost function, model |
| **objective value** | The number under `objective_key`. Lower is better. | `objective_value()` | score, cost, fitness, result |
| **incumbent** | The best value known so far. | BO literature | the best, current best |
| **stalled** | A round that did not beat the incumbent by the fraction `min_improvement` of its magnitude. | this library | flat, failed, wasted |
| **results file** | The gzipped pickle `save` writes. | this library | checkpoint, state file, database |

**study**, not task.
A study is not a unit of work.
One study expands into thousands of real tasks,
so to call it a task collides with the one word
that has to stay unambiguous.

**propose** stays as a verb,
and so does `PROPOSE_SECONDS_KEY`.
What it produces is a **candidate**.

**sweep** is retired, in prose and in identifiers alike.
The word is **exploration**, in a tutorial too,
because rule 4 leaves no room for a second word for the same thing.

## Names that changed

This table is what moved,
for anyone who reads an older branch, an older log file
or a program written against an older release.

| Was | Is |
| --- | --- |
| `ExplorationTask`, `OptimizationTask` | `ExplorationStudy`, `OptimizationStudy` |
| `tasks=` argument and `.tasks` attribute on the two space classes | `studies=` and `.studies` |
| `min_search_iterations`, `max_search_iterations` | `min_search_rounds`, `max_search_rounds` |
| `from slurm_workflows import ExploreSpaceSobolQMC` and the other search names, before `slurm-workflows` 5.0 | `from slurm_workflows_optimize import ExploreSpaceSobolQMC` |
| `slurm_workflows.search_space`, `slurm_workflows.explore_space`, `slurm_workflows.optimize_space_botorch` | `slurm_workflows_optimize.search_space`, `slurm_workflows_optimize.explore_space`, `slurm_workflows_optimize.optimize_space_botorch` |
| `pip install "slurm-workflows[botorch]"` | `pip install "slurm-workflows-optimize[botorch]"` |

## Applying this

**In prose.**
Pick the word from the tables and keep it for the whole document.
Where two senses meet in one paragraph, qualify both,
even where one of them is clear on its own.

**In identifiers.**
A name carries the same word the prose does.
A study's settings live on a `*Study` dataclass,
and a list of them is `studies`, never `tasks`.

**In error messages.**
Error messages reach a user who read nothing else,
so they carry the fullest form,
and they name the study they are about.

## Related

- [Developer notes](developer-notes.md), for why the code is the way it is
- [Batch Bayesian optimization](explanation/batch-bayesian-optimization.md),
    which uses this vocabulary for a user
