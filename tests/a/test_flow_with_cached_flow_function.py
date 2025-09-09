# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import AsyncMock

from flow_compose.a import flow, flow_function, FlowFunction

greet_hello_world_mock = AsyncMock()
greet_using_greeting_mock = AsyncMock()


@flow_function(cached=True)
async def greeting_hello_world() -> str:
    await greet_hello_world_mock()
    return "Hello World!"


@flow_function()
async def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    greeting_once = await greeting()
    greeting_twice = await greeting()
    assert greeting_once == greeting_twice
    await greet_using_greeting_mock(greeting_once)


@flow(
    greeting=greeting_hello_world,
)
async def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    await greet()


class TestFlowWithFunctionComposingCachedFunction(unittest.IsolatedAsyncioTestCase):
    async def test_flow_with_function_composing_cached_function(self):
        await hello_world()
        greet_using_greeting_mock.assert_called_once_with("Hello World!")
        greet_hello_world_mock.assert_called_once_with()

        greet_using_greeting_mock.reset_mock()
        greet_hello_world_mock.reset_mock()

        await hello_world()
        greet_using_greeting_mock.assert_called_once_with("Hello World!")
        greet_hello_world_mock.assert_called_once_with()
