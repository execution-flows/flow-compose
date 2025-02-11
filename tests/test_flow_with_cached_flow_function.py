# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from flow_compose import flow, flow_function
from flow_compose.implementation.flow_function import FlowFunction

greet_hello_world_mock = Mock()
greet_using_greeting_mock = Mock()


@flow_function(cached=True)
def greeting_hello_world() -> str:
    greet_hello_world_mock()
    return "Hello World!"


@flow_function()
def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    greeting_once = greeting()
    greeting_twice = greeting()
    assert greeting_once == greeting_twice
    greet_using_greeting_mock(greeting_once)


@flow(
    greeting=greeting_hello_world,
)
def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    greet()


class TestFlowWithFunctionComposingCachedFunction(unittest.TestCase):
    def test_flow_with_function_composing_cached_function(self):
        hello_world()
        greet_using_greeting_mock.assert_called_once_with("Hello World!")
        greet_hello_world_mock.assert_called_once_with()

        greet_using_greeting_mock.reset_mock()
        greet_hello_world_mock.reset_mock()

        hello_world()
        greet_using_greeting_mock.assert_called_once_with("Hello World!")
        greet_hello_world_mock.assert_called_once_with()
