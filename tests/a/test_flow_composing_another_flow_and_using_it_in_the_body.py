# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import AsyncMock

from flow_compose.a import flow, flow_function, FlowFunction, Flow

hello_world_greeting_mock = AsyncMock()
greeting_hello_world_mock = AsyncMock()
hello_world_2_mock = AsyncMock()


@flow_function()
async def greeting_hello_world() -> str:
    await greeting_hello_world_mock()
    return "Hello, World!"


@flow(
    greeting=greeting_hello_world,
)
async def hello_world_greeting(greeting: FlowFunction[str]) -> str:
    result_greeting = await greeting()
    await hello_world_greeting_mock(result_greeting)
    return result_greeting


@flow(
    greeting=Flow(hello_world_greeting),
)
async def hello_world(greeting: FlowFunction[str]) -> None:
    await hello_world_2_mock(await greeting())


class TestFlowComposingAnotherFlowAndUsingItInTheBody(unittest.IsolatedAsyncioTestCase):
    async def test_flow_composing_another_flow_and_using_it_in_the_body(self):
        await hello_world()
        greeting_hello_world_mock.assert_called_once()
        hello_world_greeting_mock.assert_called_once_with("Hello, World!")
        hello_world_2_mock.assert_called_once_with("Hello, World!")
