# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import AsyncMock

from flow_compose.a import flow, flow_function, FlowFunction

greet_hello_world_mock = AsyncMock()


@flow_function()
async def greet_hello_world(greeting: str) -> None:
    await greet_hello_world_mock(greeting)


@flow()
async def hello_world(
    greeting: str, greet: FlowFunction[None] = greet_hello_world
) -> None:
    await greet(greeting)


class TestFlowWithNonFlowFunctionArgument(unittest.IsolatedAsyncioTestCase):
    async def test_flow_with_non_flow_function_argument(self):
        await hello_world("Hello, World!")
        greet_hello_world_mock.assert_called_once_with("Hello, World!")
