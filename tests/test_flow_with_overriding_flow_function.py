# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from flow_compose import flow, flow_function, FlowFunction

greet_hello_world_mock = Mock()
greet_hello_world2_mock = Mock()
greet_using_greeting_mock = Mock()


@flow_function()
def greeting_hello_world() -> str:
    greet_hello_world_mock()
    return "Hello World!"


@flow_function()
def greeting_hello_world2() -> str:
    greet_hello_world2_mock()
    return "Hello World2!"


@flow_function()
def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    greet_using_greeting_mock(greeting())


@flow(
    greeting=greeting_hello_world,
    greet=greet_using_greeting,
)
def hello_world(
    greet: FlowFunction[None],
    greeting: FlowFunction[str] = greeting_hello_world2,
) -> None:
    greet()
    greeting()


class TestFlowWithOverridingFlowFunction(unittest.TestCase):
    def test_flow_with_overriding_flow_function(self):
        hello_world()
        greet_using_greeting_mock.assert_called_once()
        greet_hello_world_mock.assert_called_once()
        greet_hello_world2_mock.assert_called_once()
