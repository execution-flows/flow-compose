# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import inspect
from collections.abc import Callable
from typing import Any, Awaitable

from flow_compose.extensions.makefun_extension import with_signature
from flow_compose.implementation.classes.a.flow_function import FlowFunction
from flow_compose.implementation.classes.a.flow_function_invoker import (
    FlowFunctionInvoker,
)
from flow_compose.implementation.classes.base import FlowContext
from flow_compose.implementation.classes.base.flow_function_invoker import (
    EMPTY_FLOW_CONTEXT,
)
from flow_compose.implementation.decorators.base.flow_function import (
    get_flow_function_parameters,
    flow_function_with_flow_context_common,
)
from flow_compose.types import ReturnType


def decorator(
    cached: bool = False,
) -> Callable[[Callable[..., Awaitable[ReturnType]]], FlowFunction[ReturnType]]:
    def wrapper(
        wrapped_flow_function: Callable[..., Awaitable[ReturnType]],
    ) -> FlowFunction[ReturnType]:
        flow_function_parameters = get_flow_function_parameters(
            wrapped_flow_function=wrapped_flow_function,
        )

        @with_signature(
            func_name=wrapped_flow_function.__name__,
            func_signature=inspect.Signature(
                flow_function_parameters.non_flow_functions_parameters
                + [
                    inspect.Parameter(
                        name="__flow_context",
                        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=FlowContext,
                        default=EMPTY_FLOW_CONTEXT,
                    )
                ]
            ),
        )
        async def flow_function_with_flow_context(
            __flow_context: FlowContext, *args: Any, **kwargs: Any
        ) -> ReturnType:
            flow_function_with_flow_context_common(
                __flow_context=__flow_context,
                flow_function_parameters=flow_function_parameters,
                wrapped_flow_function=wrapped_flow_function,
                kwargs=kwargs,
                flow_function_invoker_class=FlowFunctionInvoker,
            )

            return await wrapped_flow_function(*args, **kwargs)

        return FlowFunction(flow_function_with_flow_context, cached=cached)

    return wrapper
