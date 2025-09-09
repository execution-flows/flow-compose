# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import AsyncMock

from flow_compose.a import flow, flow_function, FlowFunction

greet_hello_world_mock = AsyncMock()
greet_hello_world2_mock = AsyncMock()
greet_using_greeting_mock = AsyncMock()


@flow_function()
async def greeting_hello_world() -> str:
    await greet_hello_world_mock()
    return "Hello World!"


@flow_function()
async def greeting_hello_world2() -> str:
    await greet_hello_world2_mock()
    return "Hello World2!"


@flow_function()
async def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    await greet_using_greeting_mock(await greeting())


@flow(
    greeting=greeting_hello_world,
    greet=greet_using_greeting,
)
async def hello_world(
    greet: FlowFunction[None],
    greeting: FlowFunction[str] = greeting_hello_world2,
) -> None:
    await greet()
    await greeting()


class TestFlowWithOverridingFlowFunction(unittest.IsolatedAsyncioTestCase):
    async def test_flow_with_overriding_flow_function(self):
        await hello_world()
        greet_using_greeting_mock.assert_called_once()
        greet_hello_world_mock.assert_called_once()
        greet_hello_world2_mock.assert_called_once()
