# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import AsyncMock

from flow_compose.a import flow, flow_function, FlowFunction, Flow

hello_world_greeting_mock = AsyncMock()
greeting_hello_world_mock = AsyncMock()


@flow_function()
async def greeting_hello_world() -> str:
    await greeting_hello_world_mock()
    return "Hello, World!"


@flow_function()
async def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    await greeting()


@flow(
    greeting=greeting_hello_world,
)
async def hello_world_greeting(greeting: FlowFunction[str]) -> str:
    result_greeting = await greeting()
    await hello_world_greeting_mock(result_greeting)
    return result_greeting


@flow(
    greeting=Flow(hello_world_greeting, cached=True),
)
async def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    await greet()
    await greet()


class TestFlowComposingAnotherCachedFlow(unittest.IsolatedAsyncioTestCase):
    async def test_flow_composing_another_cached_flow(self):
        await hello_world()
        greeting_hello_world_mock.assert_called_once()
        hello_world_greeting_mock.assert_called_once_with("Hello, World!")
