# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import inspect
from typing import Callable, Any

from extensions.makefun_extension import with_signature
from flow_compose.types import (
    ReturnType,
    FlowContext,
    FlowFunction,
    FlowFunctionInvoker,
)

_FLOW_RUN_ID: int = 0


def annotation(
    **flow_functions_configuration: FlowFunction[Any],
) -> Callable[[Callable[..., ReturnType]], Callable[..., ReturnType]]:
    def wrapper(wrapped_flow: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
        global _FLOW_RUN_ID
        all_parameters = inspect.signature(wrapped_flow).parameters.values()
        flow_functions_parameters = []
        non_flow_functions_parameters = []

        # the next flag tells us when we are in flow_function arguments
        flow_functions_argument_found = False
        for parameter in all_parameters:
            if not callable(parameter.default):
                if flow_functions_argument_found:
                    raise AssertionError(
                        "flow has to have all non-flow-function arguments before flow function arguments."
                    )
                non_flow_functions_parameters.append(parameter)
                continue

            flow_functions_argument_found = True
            flow_functions_parameters.append(parameter)

        @with_signature(
            func_name=wrapped_flow.__name__,
            func_signature=inspect.Signature(non_flow_functions_parameters),
        )
        def flow_invoker(**kwargs: Any) -> ReturnType:
            global _FLOW_RUN_ID
            _FLOW_RUN_ID += 1

            flow_context = FlowContext()

            cached_flow_functions: list[FlowFunction[Any]] = []

            for configured_flow_function in flow_functions_configuration:
                flow_context[configured_flow_function] = FlowFunctionInvoker(
                    flow_function=flow_functions_configuration[
                        configured_flow_function
                    ],
                    flow_context=flow_context,
                )
                if flow_functions_configuration[configured_flow_function].cached:
                    cached_flow_functions.append(
                        flow_functions_configuration[configured_flow_function]
                    )

            for flow_function_parameter in flow_functions_parameters:
                if flow_function_parameter.name in flow_context:
                    raise AssertionError(
                        f"{flow_function_parameter.name}: FlowFunction is already defined in flow context."
                    )
                flow_context[flow_function_parameter.name] = FlowFunctionInvoker(
                    flow_function=flow_function_parameter.default,
                    flow_context=flow_context,
                )
                if flow_function_parameter.default.cached:
                    cached_flow_functions.append(flow_function_parameter.default)
                kwargs[flow_function_parameter.name] = flow_context[
                    flow_function_parameter.name
                ]

            return wrapped_flow(**kwargs)

        return flow_invoker

    return wrapper
