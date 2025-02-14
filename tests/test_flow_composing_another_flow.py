# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from flow_compose import flow, flow_function, FlowFunction, Flow

hello_world_greeting_mock = Mock()
greeting_hello_world_mock = Mock()
greet_using_greeting_mock = Mock()


@flow_function()
def greeting_hello_world() -> str:
    greeting_hello_world_mock()
    return "Hello, World!"


@flow_function()
def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    greet_using_greeting_mock(greeting())


@flow(
    greeting=greeting_hello_world,
)
def hello_world_greeting(greeting: FlowFunction[str]) -> str:
    result_greeting = greeting()
    hello_world_greeting_mock(result_greeting)
    return result_greeting


@flow(
    greeting=Flow(hello_world_greeting),
)
def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    greet()


class TestFlowComposingAnotherFlow(unittest.TestCase):
    def test_flow_composing_another_flow(self):
        hello_world()
        greeting_hello_world_mock.assert_called_once()
        hello_world_greeting_mock.assert_called_once_with("Hello, World!")
        greet_using_greeting_mock.assert_called_once_with("Hello, World!")
