# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from typing import NewType
from unittest.mock import AsyncMock

from flow_compose.a import flow, flow_function, FlowFunction, Flow, FlowArgument

greeting_hello_world_mock = AsyncMock()
greet_using_greeting_mock = AsyncMock()

Index = NewType("Index", int)


@flow_function()
async def greeting_hello_world(index: FlowFunction[Index]) -> str:
    await greeting_hello_world_mock()
    return f"Hello, World! - {await index()}"


@flow_function()
async def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    await greet_using_greeting_mock(await greeting())


@flow(
    index=FlowArgument(Index),
    greeting=greeting_hello_world,
)
async def hello_world_greeting(greeting: FlowFunction[str]) -> str:
    return await greeting()


@flow(
    index=FlowArgument(Index),
    greeting=Flow(hello_world_greeting),
)
async def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    await greet()


class TestFlowComposingAnotherFlowWithNewTypeFlowArgumentNotUsedInBody(
    unittest.IsolatedAsyncioTestCase
):
    async def test_flow_composing_another_flow_with_new_type_flow_argument_not_used_in_body(
        self,
    ):
        await hello_world(index=11)
        greeting_hello_world_mock.assert_called_once()
        greet_using_greeting_mock.assert_called_once_with("Hello, World! - 11")
