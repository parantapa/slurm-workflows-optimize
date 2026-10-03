# slurm-workflows-optimize: an optimization and hyperparameter tuning framework for slurm-workflows

`slurm-workflows-optimize` searches a parameter space
across a pool of workers on a Slurm cluster.
It evaluates an objective function at many points at once,
and keeps every point it evaluated with what the objective returned.

It builds on [`slurm-workflows`](https://github.com/parantapa/slurm-hpc-workflows),
which runs the pool.
You set up a `SlurmPilotExecutor` and its job groups as usual,
and hand the executor to one of two classes:

- `ExploreSpaceSobolQMC` evaluates a scrambled Sobol' design over a space,
    a quasi-Monte Carlo (QMC) exploration with no model behind it.
- `OptimizeSpaceBotorch` runs a batch Bayesian search with botorch.
    Each round fits a Gaussian process
    and evaluates a whole batch of candidate points at once.

## Installation

A run needs:

- Python >= 3.12
- Access to a Slurm cluster (`sbatch`, `squeue`, `scancel` on `PATH`)
- The [`ds-service`](https://github.com/parantapa/ds-service) binary on `PATH`

```sh
pip install -U slurm-workflows-optimize
# For OptimizeSpaceBotorch:
pip install -U "slurm-workflows-optimize[botorch]"
```

Either line installs `slurm-workflows` as well.
The `botorch` extra brings in botorch and torch.
Leave it out if you only explore,
and you leave torch out with it.

To set up on UVA's Rivanna cluster, follow
[How to install slurm-workflows on Rivanna](https://github.com/parantapa/slurm-hpc-workflows/blob/main/docs/how-to-guides/install-on-rivanna.md),
then install this package into the same environment.

Before `slurm-workflows` 5.0, these classes and the search space types
were part of the `slurm_workflows` package.
Import them from `slurm_workflows_optimize` now.

## Usage

This exploration estimates $\pi$ from 4096 points of the unit square.
Replace the Slurm account (`-A`), the partition (`-p`)
and the setup script with the ones for your cluster.
The driver must run on a node with the `ib0` interface.

```python
import math

from ds_service_client import DsServiceServer
from slurm_workflows import SlurmPilotExecutor
from slurm_workflows_optimize import (
    ExplorationStudy,
    ExploreSpaceSobolQMC,
    FloatRange,
)


def inside_quarter_circle(x: float, y: float) -> dict[str, float]:
    # 4 inside the quarter circle and 0 outside, so the mean estimates pi.
    return {"score": 4.0 if math.hypot(x, y) <= 1.0 else 0.0}


SETUP_SCRIPT = """
module load gcc/14.2.0
conda activate my-env
"""

with DsServiceServer(interface="ib0") as ds_service:
    ds_service.wait_until_ready()

    with SlurmPilotExecutor("estimate-pi", ds_service.address) as executor:
        executor.define_job_group(
            name="cpu",
            sbatch_args=["-A my_alloc", "-p standard", "-t 01:00:00"],
            setup_script=SETUP_SCRIPT,
        )
        executor.scale_jobs("cpu", 4)

        exploration = ExploreSpaceSobolQMC(
            [
                ExplorationStudy(
                    name="pi",
                    space={"x": FloatRange(0.0, 1.0), "y": FloatRange(0.0, 1.0)},
                    objective=inside_quarter_circle,
                    objective_queue="cpu",
                    num_exploration_points=4096,
                    seed=20260907,
                    objective_key="score",
                )
            ],
            executor,
        )
        exploration.run()
        exploration.save("pi.pkl.gz")

scores = exploration.results["pi"].values
print(sum(scores) / len(scores))
```

The exploration submits every point as a task on the `cpu` queue,
waits for all of them,
and writes every point and its result to `pi.pkl.gz`.
The last line it prints is the estimate:

```text
3.14453125
```

`OptimizeSpaceBotorch` can start a search from a file like that one.

## Documentation

| Document | What it covers |
| --- | --- |
| [Computing pi with a Sobol' QMC exploration](docs/tutorials/computing-pi-qmc.md) | Using `ExploreSpaceSobolQMC` to create a space-filling design and evaluate it. |
| [Optimizing Himmelblau's function](docs/tutorials/optimizing-himmelblau.md) | Using `OptimizeSpaceBotorch` to run a batch Bayesian search. |
| [How to resume a search](docs/how-to-guides/resume-a-search.md) | Carrying a search on across a Slurm time limit. |
| [`ExploreSpaceSobolQMC`](docs/reference/explore-space.md) | The Sobol' exploration and its study fields. |
| [`OptimizeSpaceBotorch`](docs/reference/optimize-space.md) | The batch Bayesian search, its study fields, and its stopping rule. |
| [The results file](docs/reference/results-file.md) | The file both space classes write, and `load_results`. |
| [Search spaces](docs/reference/search-space.md) | `IntRange`, `FloatRange` and `CategoricalRange`. |
| [The objective](docs/reference/objective.md) | The contract an objective function meets, and what a failed evaluation does to a run. |
| [Batch Bayesian optimization](docs/explanation/batch-bayesian-optimization.md) | Why a search has rounds, where the fit runs, and when it is worth the overhead. |

The [`slurm-workflows` documentation](https://github.com/parantapa/slurm-hpc-workflows#documentation)
covers the executor, job groups, the workers and `swtop`.

## For contributors

| Document | What it covers |
| --- | --- |
| [Developer notes](docs/developer-notes.md) | The layout of the code, where each kind of documentation goes, what this package needs from `slurm-workflows`, and the conventions a change must follow. |
| [Terminology](docs/terminology.md) | The words this project uses for the search, and where the rest of the vocabulary lives. |
| [How to run the tests](docs/how-to-run-tests.md) | Running the suite, where its fixtures come from, and what it runs for real. |

## License

MIT. See [LICENSE](LICENSE).
