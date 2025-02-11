# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from flow_compose import flow, flow_function
from flow_compose.implementation.flow_function import FlowFunction

greet_hello_world_mock = Mock()
greet_using_greeting_mock = Mock()


@flow_function()
def greeting_hello_world(index: int) -> str:
    greet_hello_world_mock(index)
    return f"Hello World! - {index}"


@flow_function()
def greet_using_greeting(index: int, greeting: FlowFunction[str]) -> None:
    greet_using_greeting_mock(greeting(index=index))


@flow(
    greeting=greeting_hello_world,
)
def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    greet(index=11)


class TestFlowWithFunctionComposingAnotherFunctionWithArguments(unittest.TestCase):
    def test_flow_with_function_using_another_function(self):
        hello_world()
        greet_using_greeting_mock.assert_called_once_with("Hello World! - 11")
        greet_hello_world_mock.assert_called_once_with(11)
