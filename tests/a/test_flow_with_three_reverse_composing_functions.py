# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import AsyncMock

from flow_compose.a import flow, flow_function, FlowFunction

composing1_mock = AsyncMock()
composing2_mock = AsyncMock()
composing3_mock = AsyncMock()


@flow_function()
async def composing3_impl() -> str:
    await composing3_mock()
    return "Hello world!"


@flow_function()
async def composing2_impl(composing3: FlowFunction[str]) -> str:
    await composing2_mock()
    return await composing3()


@flow_function()
async def composing1_impl(composing2: FlowFunction[str]) -> None:
    await composing1_mock(await composing2())


@flow(
    composing2=composing2_impl,
    composing3=composing3_impl,
)
async def composing_three_flow(
    composing1: FlowFunction[None] = composing1_impl,
) -> None:
    await composing1()


class TestFlowWithFThreeReverseComposingFunctions(unittest.IsolatedAsyncioTestCase):
    async def test_flow_with_function_using_another_function(self):
        await composing_three_flow()
        composing1_mock.assert_called_once_with("Hello world!")
        composing2_mock.assert_called_once()
        composing3_mock.assert_called_once()
