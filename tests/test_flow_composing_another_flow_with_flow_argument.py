# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import unittest
from unittest.mock import Mock

from flow_compose import flow, flow_function, FlowFunction, Flow, FlowArgument

hello_world_greeting_mock = Mock()
greeting_hello_world_mock = Mock()
greet_using_greeting_mock = Mock()


@flow_function()
def greeting_hello_world() -> str:
    greeting_hello_world_mock()
    return "Hello, World!"


@flow_function()
def greet_using_greeting(index: int, greeting: FlowFunction[str]) -> None:
    greet_using_greeting_mock(greeting(index=index))


@flow(
    index=FlowArgument(int),
    greeting=greeting_hello_world,
)
def hello_world_greeting(index: FlowArgument[int], greeting: FlowFunction[str]) -> str:
    result_greeting = f"{greeting()} - {index()}"
    hello_world_greeting_mock(result_greeting)
    return result_greeting


@flow(
    greeting=Flow(hello_world_greeting),
)
def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    greet(11)


class TestFlowComposingAnotherFlowWithFlowArgument(unittest.TestCase):
    def test_flow_composing_another_flow_with_flow_argument(self) -> None:
        hello_world()
        greeting_hello_world_mock.assert_called_once()
        hello_world_greeting_mock.assert_called_once_with("Hello, World! - 11")
        greet_using_greeting_mock.assert_called_once_with("Hello, World! - 11")
