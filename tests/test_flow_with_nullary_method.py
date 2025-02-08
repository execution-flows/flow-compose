# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from fyco import flow, flow_method

greet_hello_world_mock = Mock()


@flow_method
def greet_hello_world() -> None:
    greet_hello_world_mock()


@flow()
def hello_world(greet=greet_hello_world) -> None:
    greet()


class TestFlowWithNullaryMethod(unittest.TestCase):
    def test_flow_with_nullary_method(self):
        hello_world()
        greet_hello_world_mock.assert_called_once()
