# `ExploreSpaceSobolQMC`

[<- back to the main README](../../README.md)

`slurm_workflows_optimize.explore_space`:
the Sobol' quasi-Monte-Carlo exploration and its study dataclass.

## `ExploreSpaceSobolQMC(studies, executor, num_exploration_points=None)`

```python
from slurm_workflows_optimize import ExplorationStudy, ExploreSpaceSobolQMC

exploration = ExploreSpaceSobolQMC(studies, executor, num_exploration_points=None)
```

Draws a Sobol' design over each space it is given,
evaluates every point of every design across the pool,
and keeps what came back.
`studies` is a list of `ExplorationStudy` objects, one per space.
`ExploreSpaceSobolQMC` submits them together,
so a small study does not wait for a large one.
`num_exploration_points` is the count for studies that do not carry their own.

It needs neither botorch nor torch, on the driver or on the workers.

## `ExplorationStudy`

| Field | Meaning |
| --- | --- |
| `name` | Names the study. Keys the results and labels its tasks on the queue. |
| `space` | The search space: one entry per objective argument. See [Search spaces](search-space.md). |
| `objective` | The function to evaluate. Its argument names must match the space's keys. |
| `objective_queue` | Queue, or queues, the evaluations go to. |
| `num_exploration_points` | Points to draw. Truncated down to a power of two. Optional if the exploration carries a default. |
| `seed` | Optional. The same seed redraws the same design. Without one, `ExploreSpaceSobolQMC` draws a seed and prints it. |
| `objective_key` | Which entry of the objective's result is the value. `"objective"` by default. |
| `extra_objective_kwargs` | Extra arguments passed to the objective and not varied. |
| `priority` | The priority of every task the study submits. The highest priority runs first. `0.0` by default. |

`ExploreSpaceSobolQMC` floors the point count to a power of two.
A Sobol' sequence is balanced at that prefix length.
A study that asks for 100 points on 100 workers evaluates 64,
and leaves 36 workers idle.

The objective contract is the same for both classes:
see [The objective](objective.md).
What a failed evaluation does to a run is the same too:
see [Failures](objective.md#failures).

## Methods

| Method | What it does |
| --- | --- |
| `design(name)` | The points a study will evaluate, without evaluating them. |
| `dim(name)` | How many dimensions a study's space has. |
| `run()` | Submits every point of every study and blocks until all are back. |
| `best_point(name)` | `(params, value)` of the lowest value the study measured. |
| `best_output(name)` | The objective's whole result at that point. |
| `save(path)` | Writes the points, values and outputs to a gzipped pickle. See [The results file](results-file.md). |

```python
exploration = ExploreSpaceSobolQMC(
    [ExplorationStudy("demo", SPACE, objective, "cpu", 4096, seed=1)],
    executor,
)
exploration.run()
exploration.save("explore.pkl.gz")

result = exploration.results["demo"]   # points, values, outputs, unit_points
```

A second call to `run()` re-evaluates the same design:
the seed decides the draw, so there is no "next 4096 points".
It appends to `results`,
so `results` and the file `save()` writes then hold every point twice.
A different seed draws a different design.

## Attributes

| Attribute | What it holds |
| --- | --- |
| `results[name]` | Four index-aligned lists, in submission order: `points`, `values`, `outputs` and `unit_points`. `values` holds the values that rank the points, and `outputs` the whole results. `unit_points` holds the points in the unit cube. |
| `studies` | The study list with the point count and seed filled in. `ExploreSpaceSobolQMC` leaves the caller's own `ExplorationStudy` objects alone. |

## Related

- [Search spaces](search-space.md)
- [The objective](objective.md)
- [The results file](results-file.md)
- [`SlurmPilotExecutor`](https://github.com/parantapa/slurm-hpc-workflows/blob/main/docs/reference/executor.md)
