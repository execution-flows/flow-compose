# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import AsyncMock

from flow_compose.a import flow, flow_function, FlowFunction, Flow

hello_world_greeting_mock = AsyncMock()
greeting_hello_world_mock = AsyncMock()
greet_using_greeting_mock = AsyncMock()


@flow_function()
async def greeting_hello_world() -> str:
    await greeting_hello_world_mock()
    return "Hello, World!"


@flow_function()
async def greet_using_greeting(index: int, greeting: FlowFunction[str]) -> None:
    await greet_using_greeting_mock(await greeting(index=index))


@flow()
async def hello_world_greeting(
    index: int, index2: int = 13, greeting: FlowFunction[str] = greeting_hello_world
) -> str:
    result_greeting = f"{await greeting()} - {index} - {index2}"
    await hello_world_greeting_mock(result_greeting)
    return result_greeting


@flow(
    greeting=Flow(hello_world_greeting),
)
async def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    await greet(11)


class TestFlowComposingAnotherFlowWithNonFlowArgumentDefaultValue(
    unittest.IsolatedAsyncioTestCase
):
    async def test_flow_composing_another_flow_with_non_flow_argument_default_value(
        self,
    ):
        await hello_world()
        greeting_hello_world_mock.assert_called_once()
        hello_world_greeting_mock.assert_called_once_with("Hello, World! - 11 - 13")
        greet_using_greeting_mock.assert_called_once_with("Hello, World! - 11 - 13")
