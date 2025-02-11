# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from flow_compose import flow, flow_function, FlowFunction

greet_hello_world_mock = Mock()


@flow_function(None)
def greet_hello_world() -> None:
    greet_hello_world_mock()


@flow(None)
def hello_world(greet: FlowFunction[None] = greet_hello_world) -> None:
    greet()


class TestFlowWithNullaryFunction(unittest.TestCase):
    def test_flow_with_nullary_function(self):
        hello_world()
        greet_hello_world_mock.assert_called_once()
