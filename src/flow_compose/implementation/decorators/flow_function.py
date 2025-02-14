# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import inspect
from collections.abc import Callable
from typing import Any

from flow_compose.extensions.makefun_extension import with_signature
from flow_compose.implementation.classes.flow_function import FlowFunction
from flow_compose.implementation.classes.flow_function_invoker import (
    FlowFunctionInvoker,
    FlowContext,
)
from flow_compose.implementation.helpers import is_parameter_subclass_type
from flow_compose.types import ReturnType

_EMPTY_FLOW_CONTEXT = FlowContext()


def decorator(
    cached: bool = False,
) -> Callable[[Callable[..., ReturnType]], FlowFunction[ReturnType]]:
    def wrapper(
        wrapped_flow_function: Callable[..., ReturnType],
    ) -> FlowFunction[ReturnType]:
        all_parameters = inspect.signature(wrapped_flow_function).parameters.values()
        flow_functions_parameters = []
        non_flow_functions_parameters = []

        # the next flag tells us when we are in flow_function arguments
        flow_functions_argument_found = False
        for parameter in all_parameters:
            if not is_parameter_subclass_type(parameter, FlowFunction):
                if flow_functions_argument_found:
                    raise AssertionError(
                        "flow function has to have all non-flow-function arguments before flow function arguments."
                    )
                non_flow_functions_parameters.append(
                    inspect.Parameter(
                        name=parameter.name,
                        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=parameter.annotation,
                        default=parameter.default,
                    )
                )
                continue

            flow_functions_argument_found = True
            flow_functions_parameters.append(parameter)

        @with_signature(
            func_name=wrapped_flow_function.__name__,
            func_signature=inspect.Signature(
                non_flow_functions_parameters
                + [
                    inspect.Parameter(
                        name="__flow_context",
                        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=FlowContext,
                        default=_EMPTY_FLOW_CONTEXT,
                    )
                ]
            ),
        )
        def flow_function_with_flow_context(
            __flow_context: FlowContext, *args: Any, **kwargs: Any
        ) -> ReturnType:
            flow_context = __flow_context
            missing_flow_function_configurations: list[str] = []
            for parameter in flow_functions_parameters:
                if (
                    not isinstance(parameter.default, FlowFunction)
                    and parameter.name not in flow_context
                ):
                    missing_flow_function_configurations.append(parameter.name)
                    continue

                kwargs[parameter.name] = (
                    FlowFunctionInvoker(
                        flow_function=parameter.default,
                        flow_context=flow_context,
                    )
                    if isinstance(parameter.default, FlowFunction)
                    else flow_context[parameter.name]
                )
            if len(missing_flow_function_configurations) > 0:
                raise AssertionError(
                    f"`{'`, `'.join(missing_flow_function_configurations)}`"
                    f" {'FlowFunction is' if len(missing_flow_function_configurations) == 1 else 'FlowFunctions are'}"
                    f" required by `{wrapped_flow_function.__name__}` FlowFunction"
                    f" but {'is' if len(missing_flow_function_configurations) == 1 else 'are'}"
                    f" missing in the flow context."
                )
            return wrapped_flow_function(*args, **kwargs)

        return FlowFunction(flow_function_with_flow_context, cached=cached)

    return wrapper
