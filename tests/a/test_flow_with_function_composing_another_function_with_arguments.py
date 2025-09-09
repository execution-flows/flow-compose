# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import AsyncMock

from flow_compose.a import flow, flow_function, FlowFunction

greet_hello_world_mock = AsyncMock()
greet_using_greeting_mock = AsyncMock()


@flow_function()
async def greeting_hello_world(index: int) -> str:
    await greet_hello_world_mock(index)
    return f"Hello World! - {index}"


@flow_function()
async def greet_using_greeting(index: int, greeting: FlowFunction[str]) -> None:
    await greet_using_greeting_mock(await greeting(index=index))


@flow(
    greeting=greeting_hello_world,
)
async def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    await greet(index=11)


class TestFlowWithFunctionComposingAnotherFunctionWithArguments(
    unittest.IsolatedAsyncioTestCase
):
    async def test_flow_with_function_using_another_function(self):
        await hello_world()
        greet_using_greeting_mock.assert_called_once_with("Hello World! - 11")
        greet_hello_world_mock.assert_called_once_with(11)
