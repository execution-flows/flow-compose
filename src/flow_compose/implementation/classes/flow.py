# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import inspect
from typing import Generic, Callable, Any

from flow_compose.implementation.classes.flow_function import FlowFunction
from flow_compose.implementation.classes.flow_argument import FlowArgument
from flow_compose.implementation.helpers import is_parameter_subclass_type
from flow_compose.types import ReturnType


class Flow(FlowFunction[ReturnType], Generic[ReturnType]):
    def __init__(
        self,
        flow: Callable[..., ReturnType],
        cached: bool = False,
    ) -> None:
        self.__name: str | None = None
        super().__init__(
            flow_function=flow,
            cached=cached,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> ReturnType:
        flow_context = kwargs["__flow_context"]
        for parameter in self.parameters:
            if (
                parameter.name not in kwargs
                and is_parameter_subclass_type(parameter, FlowArgument)
                and parameter.default is inspect.Parameter.empty
            ):
                kwargs[parameter.name] = flow_context[parameter.name]
        del kwargs["__flow_context"]
        return super().__call__(*args, **kwargs)
