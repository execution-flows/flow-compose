# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from flow_compose import flow, flow_function
from flow_compose.implementation.flow_function import FlowFunction

composing1_mock = Mock()
composing2_mock = Mock()
composing3_mock = Mock()


@flow_function()
def composing3_impl() -> str:
    composing3_mock()
    return "Hello world!"


@flow_function()
def composing2_impl(composing3: FlowFunction[str]) -> str:
    composing2_mock()
    return composing3()


@flow_function()
def composing1_impl(composing2: FlowFunction[str]) -> None:
    composing1_mock(composing2())


@flow(
    composing2=composing2_impl,
    composing3=composing3_impl,
)
def composing_three_flow(composing1: FlowFunction[None] = composing1_impl) -> None:
    composing1()


class TestFlowWithFThreeReverseComposingFunctions(unittest.TestCase):
    def test_flow_with_function_using_another_function(self):
        composing_three_flow()
        composing1_mock.assert_called_once_with("Hello world!")
        composing2_mock.assert_called_once()
        composing3_mock.assert_called_once()
