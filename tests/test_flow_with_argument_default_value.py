# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from flow_compose import flow, flow_function
from flow_compose.implementation.flow_function import FlowFunction, Argument

greet_using_greeting_mock = Mock()


@flow_function()
def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    greet_using_greeting_mock(greeting())


@flow(
    greeting=Argument(str, "Hello World!"),
)
def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    greet()


class TestFlowWithArgumentDefaultValue(unittest.TestCase):
    def test_flow_with_argument_default_value(self):
        hello_world()
        greet_using_greeting_mock.assert_called_once_with("Hello World!")

        greet_using_greeting_mock.reset_mock()

        hello_world(greeting="Hello World2!")
        greet_using_greeting_mock.assert_called_once_with("Hello World2!")
