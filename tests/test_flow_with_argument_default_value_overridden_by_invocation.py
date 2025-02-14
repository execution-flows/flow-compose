# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from flow_compose import flow, flow_function, FlowFunction, FlowArgument

greet_using_greeting_mock = Mock()


@flow_function()
def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    greet_using_greeting_mock(greeting())


@flow(
    greeting=FlowArgument(str, "Hello World!"),
)
def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    greet()


class TestFlowWithArgumentDefaultValueOverriddenByInvocation(unittest.TestCase):
    def test_flow_with_argument_default_value_overridden_by_invocation(self):
        hello_world(greeting="Hola, Mundi!")
        greet_using_greeting_mock.assert_called_once_with("Hola, Mundi!")
