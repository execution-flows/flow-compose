# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest import mock
from unittest.mock import Mock

from flow_compose import flow, flow_function
from flow_compose.implementation.flow_function import FlowFunction

greet_hello_world_mock = Mock()
greet_using_greeting_mock = Mock()


@flow_function(cached=True)
def greeting_hello_world(index: int) -> str:
    greet_hello_world_mock(index)
    return f"Hello World! - {index}"


@flow_function()
def greet_using_greeting_1(greeting: FlowFunction[str]) -> None:
    greeting_once = greeting(11)
    greeting_twice = greeting(index=11)
    assert greeting_once == greeting_twice
    greet_using_greeting_mock(greeting_once)


@flow(
    greeting=greeting_hello_world,
)
def hello_world_1(greet: FlowFunction[None] = greet_using_greeting_1) -> None:
    greet()


@flow_function()
def greet_using_greeting_2(greeting: FlowFunction[str]) -> None:
    greeting_once = greeting(index=11)
    greeting_twice = greeting(13)
    assert greeting_once != greeting_twice
    greet_using_greeting_mock(greeting_once)
    greet_using_greeting_mock(greeting_twice)


@flow(
    greeting=greeting_hello_world,
)
def hello_world_2(greet: FlowFunction[None] = greet_using_greeting_2) -> None:
    greet()


class TestFlowWithFunctionComposingCachedFunctionWithArgument(unittest.TestCase):
    def test_flow_with_function_composing_cached_function_with_argument(self):
        hello_world_1()
        greet_using_greeting_mock.assert_called_once_with("Hello World! - 11")
        greet_hello_world_mock.assert_called_once_with(11)

        greet_using_greeting_mock.reset_mock()
        greet_hello_world_mock.reset_mock()

        hello_world_2()
        greet_using_greeting_mock.assert_has_calls(
            [mock.call("Hello World! - 11"), mock.call("Hello World! - 13")]
        )
        greet_hello_world_mock.assert_has_calls([mock.call(11), mock.call(13)])
