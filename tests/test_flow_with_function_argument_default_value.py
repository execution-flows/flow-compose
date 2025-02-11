# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest

from flow_compose import flow, Argument


class TestFlowWithFunctionArgumentDefaultValue(unittest.TestCase):
    def test_flow_with_function_argument_default_value(self) -> None:
        with self.assertRaisesRegex(
            AssertionError,
            "Argument `greeting` in flow `hello_world` is not FlowFunction"
            " and is also present in the flow configuration."
            " Arguments that are not FlowFunction cannot be present in the flow configuration.",
        ):

            @flow(
                greeting=Argument(str),
            )
            def hello_world(greeting="Hello World!") -> None:
                pass
