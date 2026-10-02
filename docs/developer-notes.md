# Developer notes

[<- back to the main README](../README.md)

Notes for people working on `slurm-workflows-optimize` itself.
Everything here is about the code.
The guides the README indexes cover how to *use* the library.

`slurm-workflows-optimize` is a Python library (>=3.12)
that searches a parameter space across a pool of Slurm workers.
It does two things, both covered by those guides:
the Sobol' exploration, and the batch Bayesian optimizer.
Both run on the pilot-job executor
of [`slurm-workflows`](https://github.com/parantapa/slurm-hpc-workflows).
That separate package has
[developer notes of its own](https://github.com/parantapa/slurm-hpc-workflows/blob/main/docs/developer-notes.md).
The code here lived in `slurm_workflows` itself before `slurm-workflows` 5.0.

## Where documentation goes

User documentation lives under `docs/`,
organized by [Diataxis](https://diataxis.fr/) type.
The README is a landing page:
what the library is, how to install it,
one minimal usage example, and the index of everything else.
The README links every document, so its table is the one index.
This file does not keep a second copy of it.

```
docs/
  tutorials/        lessons: a learner runs a worked example end to end
  how-to-guides/    directions: a competent user solving one stated problem
  reference/        neutral description, one page per piece of the public surface
  explanation/      why the code is the way it is, for users
  developer-notes.md, terminology.md, how-to-run-tests.md    for contributors
```

For new user-facing documentation,
decide which of the four types it is before you decide where it goes.
Then give it a row in the README's table,
among the documents of its own type.
Keep each document inside its type.
A tutorial that stops to explain links to `explanation/` instead.
A reference page describes rather than recommends.

A reference page covers one thing a user reaches for.
The page takes its name from that class or that subject,
rather than from the module that holds it.
A new public class needs a page under `reference/`
and a row in the README's table.

The executor, the workers, `swtop` and what a run publishes
belong to the `slurm-workflows` documentation.
Link to a page there with an absolute URL
rather than copy what it says.

Nothing user-facing goes in `README.md` beyond that list.

### Docstrings, comments and this file

Prose in the source is not a third documentation set.
Each kind of prose has one job:

| Where | Carries | Never carries |
| --- | --- | --- |
| Docstring | What a caller needs: what it does, its arguments, what comes back, what it raises | Why it was built this way, how it is implemented, anything a caller cannot act on |
| Comment | What is not obvious at that line, in a sentence or two | An argument for the design, or a paragraph the docs already carry |
| `docs/` | How to use the library, and what it does | |
| This file | Why the code is the way it is: the invariants, the trade-offs, the alternatives that were tried | |

A private helper's docstring is one line that says what it does.

Where a design decision sits in both places,
the next editor changes only one of them.

## Commands

There is no CI in this repository, so nothing runs these for you.
The install and test commands are also at the top of [`how-to-run-tests.md`](how-to-run-tests.md).

The tests load fixtures from `slurm-workflows`.
To work against a checkout of `slurm-workflows` rather than a release,
install that checkout in editable mode first:

```sh
pip install -ve ../slurm-workflows    # only for a local checkout of the core
pip install -ve .[test,dev]
black src tests examples    # format
pyright                     # type-check
pytest                      # test suite
```

To build the sdist and the wheel into `dist/`,
run `python -m build`.
Then run `python -m twine check dist/*.tar.gz dist/*.whl`.
Neither `build` nor `twine` is in an extra,
so install them first.

`pyproject.toml` configures `black` and `pyright`.
`[tool.pyright]` sets the include paths and `pythonVersion`.
For this reason, run `pyright` bare.
Do not pass paths to `pyright`, or it ignores that configuration.

To run the library, start a `ds-service` server
and a `SlurmPilotExecutor` against it.
Then, on a node that can call `sbatch`,
run a driver script, such as one under `examples/`.

Deploy to clusters with `cpush`.
See `.cpush.json5` for the `rivanna` remote.

## Where things live

Paths are relative to `src/slurm_workflows_optimize/`.

| Module | Holds |
| --- | --- |
| `__init__.py` | The public API of the library. Loads the botorch module lazily. |
| `search_space.py` | Search spaces and the mapping to and from the unit cube. Imports no torch. |
| `explore_space.py` | Sobol' explorations with no model behind them, and the results file format the optimizer also reads |
| `optimize_space_botorch.py` | The botorch searches. Optional, behind the `botorch` extra. |
| `utils.py` | Helpers the two space classes share: the check on an objective's result, and formatting |

`tests/` holds the suite.
[`how-to-run-tests.md`](how-to-run-tests.md#layout) maps its files.
`examples/` holds the scripts the tutorials walk through.

`MANIFEST.in` decides what the sdist ships:
the `.py` files under `src/slurm_workflows_optimize`,
the README, the license and `pyproject.toml`.
A package data file of any other type needs a line there,
or an installed copy runs without it.

## Tools and libraries

`pyproject.toml` pins the versions and the extras.
This table says what each one is here for.

| Dependency | Used by | For |
| --- | --- | --- |
| `slurm-workflows` | `explore_space`, `optimize_space_botorch`, the tests | The executor that runs every evaluation and every fit, and the test fixtures. Pinned to one major version. See [What this package needs from slurm-workflows](#what-this-package-needs-from-slurm-workflows). |
| `scipy` | `explore_space` | `stats.qmc.Sobol` for the exploration design. The design comes back as a numpy array, and `explore_space` turns each row into a list. |
| `botorch` | `optimize_space_botorch` | The Gaussian process fit and the acquisition optimization. **Optional**, behind the `botorch` extra, and imported lazily so `import slurm_workflows_optimize` works without it. |
| `torch`, `gpytorch` | `optimize_space_botorch` | What botorch runs on, and what the `botorch` extra brings in with it. The module builds `torch` tensors, and takes the marginal log likelihood from `gpytorch`. |

Development tooling, behind the `dev` and `test` extras:

| Tool | Extra | Role |
| --- | --- | --- |
| `pytest` | `test` | The suite. See [`how-to-run-tests.md`](how-to-run-tests.md). |
| `botorch` | `test` | So the optimizer tests run rather than skip. |
| `black` | `dev` | Formatting. Configured in `pyproject.toml`. |
| `pyright` | `dev` | Type checking. Configured in `pyproject.toml`. Run it bare. |
| `setuptools_scm` | build | Deriving the version from git tags, with a `1.0.0-dev` fallback. |
| `build` | none, installed by hand | Building the sdist and the wheel. |
| `twine` | none, installed by hand | Checking and uploading the sdist and the wheel. |
| `cpush` | external | Deploying to clusters. See `.cpush.json5`. |

There is no linter beyond `pyright`.

## What this package needs from slurm-workflows

Both space classes drive the executor through its advanced interface,
and touch nothing private.
The tests lean on the fixtures that `slurm-workflows` ships.
A change to any item below is a breaking change in `slurm-workflows`,
and needs a matching release here.

| From `slurm_workflows` | Used for |
| --- | --- |
| `SlurmPilotExecutor.submit` | One task per point or per fit, with `task_priority` from the study. |
| `SlurmPilotExecutor.set_task_name` | The `<study>-explore-<i>`, `<study>-search-<round>-<i>` and `<study>-fit-<round>` names that `swtop` shows. |
| `SlurmPilotExecutor.wait` with `RaiseOnError.RAISE_AFTER_COMPLETED` | Waiting on a whole batch, and still seeing every output that came back. |
| `Task.output` | The value of one evaluation, or the failure in its place. |
| `RemoteExecutionError` | Telling a failed evaluation from a result. |
| `slurm_workflows.testing` | The `executor`, `ds_service_address`, `ds_client` and `pilot_jobs` fixtures, and the `make_worker` and `run_worker` helpers. |

The space classes do not use `map` or `map_reduce`,
the simple interface of `slurm-workflows`.
`map` returns nothing when any item fails,
and a search has to record the points that did come back.
`map` also has no per-point task names or priorities.

`pyproject.toml` pins `slurm-workflows>=5,<6`.
Raise the ceiling only after the suite passes against the new major version.

## Invariants

This section lists the things that are easy to break and quiet when broken.

### Task flow

The executor's own rules on how a wait polls, fails and reports
are under
[Task flow in the `slurm-workflows` developer notes](https://github.com/parantapa/slurm-hpc-workflows/blob/main/docs/developer-notes.md#task-flow).
Two of them matter most here.
A wait under `RAISE_AFTER_COMPLETED` waits for every task that can still finish,
and raises once at the end.
A task that the server failed because a task it waits on failed never ran.
Its output is a `RemoteExecutionError` with an empty `error_id`.

**Both space classes record what came back, even when the batch failed.**
`ExploreSpaceSobolQMC` and `OptimizeSpaceBotorch`
wait with `RAISE_AFTER_COMPLETED` and then record.
On the failure path they record what returned before they re-raise.
An exploration of a few thousand points must not lose all of them to one.
`save()` is what the next run reads.

### Search spaces (`search_space.py`)

**Never import torch or botorch here.**
This rule is the whole point of the split.
A search space is arithmetic on one value at a time,
so code that builds or tests one runs where the optimizer cannot be installed.
`tests/test_search_space.py` therefore runs without the `importorskip`
that skips every botorch test.
`optimize_space_botorch` imports only what it uses from `search_space`
and re-exports nothing.
Every importer takes a range from `search_space` alone.

**`to_unit` and `to_params` agree by the order of the space.**
A `SearchSpace` is an ordered mapping in practice,
and a unit point is a bare list of coordinates.
The column order is therefore the mapping's own iteration order.
Two spaces that hold the same ranges in a different order
are different spaces to a model fit on one of them.

### Sobol' exploration (`explore_space.py`)

**scipy's Sobol', not botorch's.**
`ExploreSpaceSobolQMC` draws with `scipy.stats.qmc.Sobol`,
so an exploration needs neither torch nor botorch,
and `tests/test_explore_space.py` runs without them.

**`run` submits every task before it waits for any of them.**
This order is what "simultaneously" means here:
one `submit` loop over every study's design, then a single `wait`.
A submit and a wait per study leaves the pool idle
whenever a small study finishes ahead of a large one.
A submit and a wait per study also serializes studies
that name different queues,
even though nothing makes them wait for each other.

**`ExploreSpaceSobolQMC` shares the shape of `OptimizeSpaceBotorch`, not its code.**
Both classes submit a batch, wait with `RAISE_AFTER_COMPLETED`,
record what came back and report the best, in their own code.
The most error-prone part sits in one place.
`utils.objective_value` is the one place that checks an objective's result,
so the four rejection messages cannot drift apart.
The rest still can.
A fix to one class belongs in the other class as well.

**`explore_space` owns the results file format.**
`load_results` reads what both `save` methods write,
and `SavedResults` says what a file holds.
The optimizer imports the reader rather than reimplementing it,
which is what keeps "the shape the explorer writes" true.
`unit_points` is deliberately not in the file.
Only the space can place a point in the unit cube,
and a stored copy can come from a different space.

The file holds plain dicts and lists, and no class of this package.
For this reason, a file that `slurm-workflows` 4.x wrote
still loads after the move to this package.
Keep it that way.
A pickled class ties every saved file to the module path of that class.

### Batch Bayesian optimization (`optimize_space_botorch.py`)

**`OptimizeSpaceBotorch` never explores.**
`OptimizeSpaceBotorch` starts from results files,
and it fails if a study has no observations in them.
That dependence on files is what makes a search resumable.
The state that has to survive a time limit is a file, not an object.
`save` writes only what its own run measured,
so the files concatenate without double counting.

**A round is two batches, not two per study.**
`OptimizeSpaceBotorch` submits every active study's fit before it waits for any,
then every active study's candidates.
The studies therefore advance in step and drop out independently,
each against its own `patience`, floor and ceiling.

- **The fit runs on a worker, not on the driver.**
  `_fit_and_propose` submits `fit_and_propose` to `optimizer_queue`
  as one task per study per round, the fit and the acquisition together.
  A fitted Gaussian process shipped back to the driver costs more than the fit did.
  Keep `fit_and_propose` a module-level function
  that takes and returns plain Python.
  Then cloudpickle sends it by reference,
  and no torch object has to survive a hop between nodes.
  A reference means the worker imports `slurm_workflows_optimize`,
  so the workers of `optimizer_queue` need this package and botorch.
  The workers of `objective_queue` need neither.
- **The four acquisition knobs belong to the study, not to the process.**
  `num_restarts`, `raw_samples`, `mc_samples` and `acqf_timeout_s`
  are `OptimizationStudy` fields with literal defaults,
  passed to every `fit_and_propose` task.
  A value read inside `fit_and_propose` is the *worker's*,
  and it ignores how the caller configured the search.
  A test either passes the knobs to the constructor
  (`make_opt(..., acqf_timeout_s=...)`) and asserts the values it passed,
  or asserts against `opt.studies[i].<knob>`,
  never against a literal.
- **Never import this module eagerly from the package `__init__.py`.**
  `OptimizeSpaceBotorch` and `OptimizationStudy` are importable
  from the package root, but through the `__getattr__` there.
  That `__getattr__` imports this module on first use,
  so `import slurm_workflows_optimize` still works without botorch installed.
  An import at the top of `__init__.py`
  makes botorch a hard dependency of the whole package.
- The module calls `optimize_acqf`, `fit_gpytorch_mll`,
  `qLogNoisyExpectedImprovement` and `fit_and_propose`
  through module globals.
  The tests monkeypatch those to assert what the code asked for,
  without paying for a real acquisition optimization.
  That works because `LocalExecutor` runs the submitted task inline,
  in the test's own process.
  The patch reaches the fit only for as long as that stays true.

## Conventions

- **After you change any Python, run `black`, then `pyright`, then `pytest`.**
  All three must be clean before you call the change done:
  `black` reports "left unchanged",
  `pyright` reports "0 errors",
  `pytest` passes.
  Run `black` first.
  `black` rewrites lines,
  so a type check before formatting
  can report positions that no longer exist.
  None of the three tools is advisory here.

  If `pyright` objects to a deliberate test double,
  say so with a `cast` and a comment.
  The comment says why the double is enough
  (see `as_executor` in `tests/test_optimize_space_botorch.py`).
  Do not silence it with a bare `# type: ignore`.
  If `pyright` objects to something in `src/`, fix the annotation instead.
- **Deprecation warnings are errors in the test suite**
  (`filterwarnings` in `pyproject.toml`).
  They are how a dependency announces a break one release ahead.
  A warning nobody reads is a break discovered at the worst moment.
  Other warnings stay warnings.
  The test suite deliberately hands botorch a constant objective in places,
  and botorch says so at runtime.
- **Prose uses semantic line breaks.**
  Break at clause boundaries, not at a column limit.
  Start a new line after each sentence,
  and at punctuation that already separates clauses (`.` `:` `,`).
  Start one before a conjunction or a preposition that opens a new phrase.
  Never end a line mid-phrase,
  on an article, a conjunction, a preposition or an auxiliary,
  which is what fixed-width wrapping produces.
  The result is a ragged right margin, and that margin is the point.
  A diff then shows only the clause that actually changed,
  instead of a whole reflowed paragraph.
  Keep lines under the usual limit as a ceiling, not a target.

  ```python
  # Wrong, wrapped at a column and broken mid-phrase:
  # The seed is the only thing that decides the design. The name is for
  # progress bars and error messages.

  # Right, one clause per line:
  # The seed is the only thing that decides the design.
  # The name is for progress bars and error messages.
  ```

  This convention governs `#` comment blocks, docstring prose,
  and every Markdown file in the repository:
  `README.md`, `docs/*.md`, and this file.
  Exempt: anything whose line structure is already meaningful.
  That covers code inside fences, Markdown tables, headings,
  and ASCII section banners (`# ---- name ----`).
- **[`terminology.md`](terminology.md) decides what a thing is called.**
  It binds prose and identifiers alike,
  so a name carries the same word the prose does.
  Where a concept has no row there, add one.
  Do not coin a second word for something the tables already name.
