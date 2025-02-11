# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from flow_compose import flow, flow_function, FlowFunction

greet_hello_world_mock = Mock()
greet_using_greeting_mock = Mock()


@flow_function(str)
def greeting_hello_world() -> str:
    greet_hello_world_mock()
    return "Hello World!"


@flow_function(None)
def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    greet_using_greeting_mock(greeting())


@flow(
    None,
    greeting=greeting_hello_world,
    greet=greet_using_greeting,
)
def hello_world(greet: FlowFunction[None]) -> None:
    greet()


class TestFlowWithAllFunctionsInConfiguration(unittest.TestCase):
    def test_flow_with_all_functions_in_configuration(self):
        hello_world()
        greet_using_greeting_mock.assert_called_once()
        greet_hello_world_mock.assert_called_once()
