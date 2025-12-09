"""Pytest configuration providing lightweight asyncio support.

The upstream project relies on ``pytest-asyncio``.  The kata environment
does not install extra dependencies, so we emulate the minimal behaviour
needed for the bundled unit tests by executing marked coroutine tests via
``asyncio.run``.
"""

from __future__ import annotations

import asyncio
import inspect

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "asyncio: execute the test function in an event loop")


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
    marker = pyfuncitem.get_closest_marker("asyncio")
    if marker is None:
        return None

    func = pyfuncitem.obj
    if not inspect.iscoroutinefunction(func):
        return None

    kwargs = {name: pyfuncitem.funcargs[name] for name in pyfuncitem._fixtureinfo.argnames}
    asyncio.run(func(**kwargs))
    return True

