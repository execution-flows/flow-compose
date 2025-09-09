# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import AsyncMock

from flow_compose.a import flow, flow_function, FlowFunction

greet_hello_world_mock_1 = AsyncMock()
greet_hello_world_mock_2 = AsyncMock()
greet_hello_world_mock_2_1 = AsyncMock()
greet_using_greeting_index_default_mock = AsyncMock()
greet_using_greeting_mock = AsyncMock()


@flow_function()
async def greeting2_value() -> str:
    return "Hello World2!"


@flow_function()
async def greeting_hello_world_1(index: int) -> str:
    await greet_hello_world_mock_1(index)
    return f"Hello World! - {index}"


@flow_function()
async def greeting_hello_world_2(index: int, greeting2: FlowFunction[str]) -> str:
    await greet_hello_world_mock_2(index)
    await greet_hello_world_mock_2_1(await greeting2())
    return f"Hello World! - {index}"


@flow_function()
async def greet_using_greeting(
    index: int, index_default: int = 13, greeting=greeting_hello_world_2
) -> None:
    await greet_using_greeting_index_default_mock(index_default)
    await greet_using_greeting_mock(await greeting(index))


@flow(
    greeting=greeting_hello_world_1,
    greeting2=greeting2_value,
)
async def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    await greet(11)


@flow(
    greeting2=greeting2_value,
)
async def hello_world_2(greet: FlowFunction[None] = greet_using_greeting) -> None:
    await greet(index=11)


class TestFlowWithFunctionComposingAnotherFunctionWithArgumentsWithDefaultValues(
    unittest.IsolatedAsyncioTestCase
):
    async def test_flow_with_function_using_another_function(self):
        await hello_world()
        greet_using_greeting_index_default_mock.assert_called_once_with(13)
        greet_using_greeting_mock.assert_called_once_with("Hello World! - 11")
        greet_hello_world_mock_1.assert_not_called()
        greet_hello_world_mock_2.assert_called_once_with(11)
        greet_hello_world_mock_2_1.assert_called_once_with("Hello World2!")

        await hello_world_2()
