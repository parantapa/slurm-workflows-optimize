# The results file

[<- back to the main README](../../README.md)

`slurm_workflows_optimize.explore_space`:
the results file both space classes write,
and `load_results`, which reads it back.

## The file

Each file is a gzipped plain pickle of data, not of code.
The study name is the key, and each entry holds `points`, `values` and `outputs`
as index-aligned lists in submission order:

```python
import gzip, pickle

with gzip.open("explore.pkl.gz", "rb") as fobj:
    results = pickle.load(fobj)

results["demo"]["points"]     # the parameters of each evaluation
```

`unit_points` is not in the file: only the space can place a point
in the unit cube.

## `load_results(paths)`

`load_results(paths)` reads saved files back.
It merges them by study name
into a `dict[str, SavedResults]`.

## Related

- [`ExploreSpaceSobolQMC`](explore-space.md)
- [`OptimizeSpaceBotorch`](optimize-space.md)
- [How to resume a search](../how-to-guides/resume-a-search.md)
