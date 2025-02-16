# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from typing import NewType

from flow_compose import flow

Greeting = NewType("Greeting", str)


@flow()
def hello_world(greeting: Greeting) -> None:
    assert greeting


class TestFlowWithNewTypeArgument(unittest.TestCase):
    def test_flow_with_new_type_argument(self):
        hello_world(
            greeting="Hello, World!",
        )
