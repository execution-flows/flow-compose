# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest import mock
from unittest.mock import AsyncMock

from flow_compose.a import flow, flow_function, FlowFunction

greet_hello_world_mock = AsyncMock()
greet_using_greeting_mock = AsyncMock()


@flow_function(cached=True)
async def greeting_hello_world(index: int) -> str:
    await greet_hello_world_mock(index)
    return f"Hello World! - {index}"


@flow_function()
async def greet_using_greeting_1(greeting: FlowFunction[str]) -> None:
    greeting_once = await greeting(11)
    greeting_twice = await greeting(index=11)
    assert greeting_once == greeting_twice
    await greet_using_greeting_mock(greeting_once)


@flow(
    greeting=greeting_hello_world,
)
async def hello_world_1(greet: FlowFunction[None] = greet_using_greeting_1) -> None:
    await greet()


@flow_function()
async def greet_using_greeting_2(greeting: FlowFunction[str]) -> None:
    greeting_once = await greeting(index=11)
    greeting_twice = await greeting(13)
    assert greeting_once != greeting_twice
    await greet_using_greeting_mock(greeting_once)
    await greet_using_greeting_mock(greeting_twice)


@flow(
    greeting=greeting_hello_world,
)
async def hello_world_2(greet: FlowFunction[None] = greet_using_greeting_2) -> None:
    await greet()


class TestFlowWithFunctionComposingCachedFunctionWithArgument(
    unittest.IsolatedAsyncioTestCase
):
    async def test_flow_with_function_composing_cached_function_with_argument(self):
        await hello_world_1()
        greet_using_greeting_mock.assert_called_once_with("Hello World! - 11")
        greet_hello_world_mock.assert_called_once_with(11)

        greet_using_greeting_mock.reset_mock()
        greet_hello_world_mock.reset_mock()

        await hello_world_2()
        greet_using_greeting_mock.assert_has_calls(
            [mock.call("Hello World! - 11"), mock.call("Hello World! - 13")]
        )
        greet_hello_world_mock.assert_has_calls([mock.call(11), mock.call(13)])
