"""Shared test fixtures."""

# The server, the fake Slurm, the executor and the in-process worker
# come from the plugin that slurm-workflows ships.
# See docs/how-to-run-tests.md.

from __future__ import annotations

import os
import signal
from types import FrameType
from typing import Generator, NoReturn

import pytest

pytest_plugins = ["slurm_workflows.testing"]


@pytest.fixture(autouse=True)
def _hang_guard() -> Generator[None]:
    """Backstop so no single test can hang the suite."""

    def on_alarm(signum: int, frame: FrameType | None) -> NoReturn:
        raise TimeoutError("test exceeded its 60s time limit")

    previous = signal.signal(signal.SIGALRM, on_alarm)
    signal.setitimer(signal.ITIMER_REAL, 60.0)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


@pytest.fixture(autouse=True)
def _restore_environ() -> Generator[None]:
    """Put `os.environ` back after each test."""

    # `PilotWorker.__init__` writes `DS_SERVER_ADDRESS`, `PILOT_WORKER_ID`
    # and the `PILOT_JOB_*` variables, and undoes none of them.
    env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(env)
