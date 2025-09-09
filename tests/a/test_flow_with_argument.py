# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import AsyncMock

from flow_compose.a import flow, flow_function, FlowFunction, FlowArgument

greet_using_greeting_mock = AsyncMock()


@flow_function()
async def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    await greet_using_greeting_mock(await greeting())


@flow(
    greeting=FlowArgument(str),
)
async def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    await greet()


class TestFlowWithArgument(unittest.IsolatedAsyncioTestCase):
    async def test_flow_with_argument(self):
        await hello_world(
            greeting="Hello World!",
        )
        greet_using_greeting_mock.assert_called_once_with("Hello World!")
