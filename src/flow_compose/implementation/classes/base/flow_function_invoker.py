# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
from typing import Generic, TypeVar, Any

from flow_compose.types import ReturnType
from flow_compose.implementation.classes.base.flow_function import FlowFunction


class FlowContext(dict[str, "FlowFunctionInvoker[Any]"]):
    pass


EMPTY_FLOW_CONTEXT = FlowContext()


FlowFunctionT = TypeVar("FlowFunctionT", bound=FlowFunction)


class FlowFunctionInvoker(Generic[FlowFunctionT, ReturnType]):
    def __init__(
        self,
        flow_function: FlowFunctionT,
        flow_context: FlowContext,
    ) -> None:
        self._flow_function = flow_function
        self._flow_context = flow_context
        self._flow_function_cache: dict[int, ReturnType] = {}


FlowFunctionInvokerT = TypeVar("FlowFunctionInvokerT", bound=FlowFunctionInvoker)
