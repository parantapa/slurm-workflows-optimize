# How to run the tests

[<- back to the main README](../README.md)

From the repository root:

```sh
pip install -ve .[test,dev]
pytest
```

To test against a local checkout of `slurm-workflows` rather than a release,
install that checkout in editable mode first:

```sh
pip install -ve ../slurm-workflows
pip install -ve .[test,dev]
pytest
```

To run one file, one class or one test, give pytest its node id:

```sh
pytest tests/test_search_space.py
pytest tests/test_search_space.py::TestIntRange
pytest tests/test_explore_space.py::TestRealExecutor
```

To leave out the tests that start a real `ds-service` server,
deselect the `integration` marker:

```sh
pytest -m "not integration"
```

The suite needs no Slurm cluster.
It has 217 tests, and it takes about 30 seconds end to end.
The botorch tests take most of that.
A test against the real server starts a `ds-service` process of its own,
and pays for that start.

The `[test]` extra installs botorch, and so torch.
That download is large.
Without botorch, `test_optimize_space_botorch.py` skips,
and the rest of the suite still runs.
`[dev]` adds `black` and `pyright`.
The gate that runs them is under Conventions
in the [developer notes](developer-notes.md#conventions).

## Where the fixtures come from

`slurm-workflows` ships its test fixtures as a pytest plugin,
`slurm_workflows.testing`.
`tests/conftest.py` loads it with one line:

```python
pytest_plugins = ["slurm_workflows.testing"]
```

The plugin gives these fixtures and helpers:

| Name | Kind | What it gives |
| --- | --- | --- |
| `ds_service_address` | fixture | The address of a private `ds-service` server for one test. |
| `ds_client` | fixture | A client against that server. |
| `fake_slurm` | fixture | A stand-in for `sbatch`, `squeue` and `scancel`. |
| `executor` | fixture | A `SlurmPilotExecutor` wired to the server and the fake Slurm. |
| `pilot_jobs` | fixture | Declares one pilot job for each named job group, as any test that waits needs. |
| `make_worker` | function | A real `PilotWorker` against a real server. |
| `run_worker` | function | Runs a worker's real main loop until it completes a given number of tasks. |

`tests/conftest.py` itself holds only what the plugin leaves to each suite:
a 60 s alarm on every test,
and a fixture that puts `os.environ` back after each test.

## What is real and what is mocked

**Slurm is mocked.**
The `fake_slurm` fixture replaces the `subprocess` module
inside `slurm_workflows.slurm_utils`.
Nothing here submits a real job.

**`ds-service` is real.**
Each test that asks for a server gets its own process on a random port.
`DsServiceServer` from `ds-service-client` starts it,
from `$DS_SERVICE_BIN` if you set it, otherwise from `ds-service` on `$PATH`.
If neither one finds the binary, the tests that need a server skip.
The tests that need no server still run,
such as the search space and `utils` tests,
and every test on `LocalExecutor`.

## Layout

Paths are relative to [`tests/`](../tests).

| File | Covers |
| --- | --- |
| `test_search_space.py` | The range types and the unit cube mapping (no botorch needed) |
| `test_explore_space.py` | `ExploreSpaceSobolQMC`: the design it draws and what it records (no botorch needed) |
| `test_utils.py` | The shared helpers |
| `test_optimize_space_botorch.py` | `OptimizeSpaceBotorch`: the observations it starts from, rounds, acquisition, search behavior, resuming (skips without botorch) |
| `conftest.py` | Loads the `slurm_workflows.testing` plugin, and adds the hang guard and the environment restore |

## Notes for future changes

- **Most tests use a stand-in executor.**
  `test_explore_space.py` and `test_optimize_space_botorch.py`
  each define a `LocalExecutor` that runs the objective inline.
  The comment on `as_executor` names the three calls
  the space classes make on it:
  `submit`, `set_task_name` and `wait`.
  A GP fit already dominates each botorch test,
  so a queue round trip adds nothing.
  `TestRealExecutor` in each file keeps the stand-in honest.
  It runs a whole exploration or a whole search
  through the real executor, the real queue and a real worker.
- **A test whose driver blocks runs its real worker in a thread.**
  The exploration and the optimizer
  both block in a wait the moment they submit.
  So nothing on the test's own thread can run the worker.
  `run_worker` stops the worker after the number of tasks it is given.
  A test that gives too high a number
  spins until the 60 s alarm ends it.
- **A wall-clock alarm bounds every test.**
  The executor's polling loop and the worker's main loop
  both run until a condition holds.
  So a regression turns a failing test into a hanging one.
  An autouse 60 s alarm in `conftest.py` limits every test.
- **Four botorch tests assert search behavior, not bookkeeping.**
  They catch a flipped sign on the objective:
  botorch maximizes, and the optimizer minimizes.
  These tests are stochastic,
  because torch's global RNG stays unseeded.
  Their margins come from measured spreads:

    - The monotone case has a median search point of 0.00
      against a 0.5 threshold,
      and a flipped sign puts that point at 0.97 or above.
    - `test_search_beats_random_search` won 12 runs out of 12,
      with a 4.6x margin.

  Assert on that median rather than the max,
  because `qLogNoisyExpectedImprovement` probes away from the incumbent
  by design.
  Single points reach 1.0 on a correct run.
  An assertion on `best_point()` does not work either.
  The exploration alone lands near the minimum,
  so `best_point()` passes even with the sign flipped.
  All four use unimodal objectives on purpose:
  an earlier Himmelblau version of the random-search comparison
  lost 1 run in 10.
- **A real-executor test declares its queue with `pilot_jobs`.**
  It also carries `@pytest.mark.integration`,
  so `-m "not integration"` leaves it out.
  A wait refuses a queue that no pilot job of the executor serves,
  even where an in-process worker drains it.
  Where one worker serves both the evaluations and the fit,
  count the fit tasks in the number given to `run_worker`:
  one per round, on top of the evaluations.
