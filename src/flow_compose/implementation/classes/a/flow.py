# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import inspect
from typing import Generic, Callable, Any, Awaitable

from flow_compose.implementation.classes.a.flow_function import FlowFunction
from flow_compose.implementation.classes.a.flow_function_invoker import (
    FlowFunctionInvoker,
)
from flow_compose.types import ReturnType


class Flow(FlowFunction[ReturnType], Generic[ReturnType]):
    def __init__(
        self,
        flow: Callable[..., Awaitable[ReturnType]],
        cached: bool = False,
    ) -> None:
        super().__init__(
            flow_function=flow,
            cached=cached,
        )

    async def __call__(self, *args: Any, **kwargs: Any) -> ReturnType:
        flow_context = kwargs["__flow_context"]
        for parameter in self.parameters:
            if parameter.name not in kwargs and (
                parameter.name in flow_context
                or parameter.default is not inspect.Parameter.empty
            ):
                if parameter.name in flow_context:
                    kwarg = flow_context[parameter.name]
                else:
                    kwarg = parameter.default
                kwargs[parameter.name] = (
                    await kwarg() if isinstance(kwarg, FlowFunctionInvoker) else kwarg
                )

        del kwargs["__flow_context"]
        return await super().__call__(*args, **kwargs)
