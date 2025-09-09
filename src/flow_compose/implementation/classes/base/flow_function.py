# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import inspect
from functools import cached_property
from typing import Generic, Callable, TypeVar

from flow_compose.types import ReturnType


class FlowFunction(Generic[ReturnType]):
    def __init__(
        self,
        flow_function: Callable[..., ReturnType],
        cached: bool,
    ):
        self._flow_function = flow_function
        self._flow_function_signature = inspect.signature(flow_function)
        self.cached = cached
        self.value: ReturnType

    @property
    def name(self) -> str:
        return self._flow_function.__name__

    @cached_property
    def parameters(self) -> list[inspect.Parameter]:
        return [p for p in self._flow_function_signature.parameters.values()]


FlowFunctionT = TypeVar("FlowFunctionT", bound=FlowFunction)  # type:ignore[type-arg]
