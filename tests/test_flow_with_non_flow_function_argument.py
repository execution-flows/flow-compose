# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from flow_compose import flow, flow_function, FlowFunction

greet_hello_world_mock = Mock()


@flow_function()
def greet_hello_world(greeting: str) -> None:
    greet_hello_world_mock(greeting)


@flow()
def hello_world(greeting: str, greet: FlowFunction[None] = greet_hello_world) -> None:
    greet(greeting)


class TestFlowWithNonFlowFunctionArgument(unittest.TestCase):
    def test_flow_with_non_flow_function_argument(self):
        hello_world("Hello, World!")
        greet_hello_world_mock.assert_called_once_with("Hello, World!")
