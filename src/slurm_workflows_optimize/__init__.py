"""Search a parameter space with slurm-workflows."""

from typing import TYPE_CHECKING, Any

from .search_space import IntRange, FloatRange, CategoricalRange
from .explore_space import (
    ExplorationStudy,
    ExploreSpaceSobolQMC,
    SavedResults,
    load_results,
)

# Never imported at runtime, since botorch is optional.
# See the developer notes, Batch Bayesian optimization.
if TYPE_CHECKING:
    from .optimize_space_botorch import OptimizationStudy, OptimizeSpaceBotorch

_BOTORCH_NAMES = ("OptimizationStudy", "OptimizeSpaceBotorch")

__all__ = [
    "IntRange",
    "FloatRange",
    "CategoricalRange",
    "ExplorationStudy",
    "ExploreSpaceSobolQMC",
    "SavedResults",
    "load_results",
    "OptimizationStudy",
    "OptimizeSpaceBotorch",
]


def __getattr__(name: str) -> Any:
    """Resolve the botorch names on first use."""
    if name in _BOTORCH_NAMES:
        from . import optimize_space_botorch

        return getattr(optimize_space_botorch, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
