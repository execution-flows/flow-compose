# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest

from flow_compose.a import flow, flow_function, FlowFunction


@flow_function()
async def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    await greeting()


@flow()
async def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    await greet()


class TestFlowWithIncompleteConfiguration(unittest.IsolatedAsyncioTestCase):
    async def test_flow_with_incomplete_configuration(self) -> None:
        with self.assertRaisesRegex(
            AssertionError,
            "`greeting` FlowFunction is required by `greet_using_greeting` FlowFunction"
            " but is missing in the flow context.",
        ):
            await hello_world()
