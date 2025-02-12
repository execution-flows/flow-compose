# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from flow_compose import flow, FlowArgument

greeting_mock = Mock()


@flow(
    greeting=FlowArgument(str),
)
def hello_world(greeting: FlowArgument[str]) -> None:
    greeting_mock(greeting())


class TestFlowWithArgumentUsedInTheFlow(unittest.TestCase):
    def test_flow_with_argument_used_in_the_flow(self):
        hello_world(
            greeting="Hello World!",
        )
        greeting_mock.assert_called_once_with("Hello World!")
