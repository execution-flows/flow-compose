# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import inspect
from collections.abc import Callable
from typing import Any, get_args

from flow_compose.extensions.makefun_extension import with_signature
from flow_compose.implementation.classes.flow_argument import FlowArgument
from flow_compose.implementation.classes.flow_function import FlowFunction
from flow_compose.implementation.classes.flow_function_invoker import (
    FlowFunctionInvoker,
    FlowContext,
)
from flow_compose.implementation.helpers import is_parameter_subclass_type
from flow_compose.types import (
    ReturnType,
)


def decorator(
    **flow_functions_configuration: FlowFunction[Any],
) -> Callable[[Callable[..., ReturnType]], Callable[..., ReturnType]]:
    def wrapper(wrapped_flow: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
        all_parameters = inspect.signature(wrapped_flow).parameters.values()
        flow_functions_parameters: list[inspect.Parameter] = []
        non_flow_functions_parameters: list[inspect.Parameter] = []
        flow_function_arguments: set[str] = set()

        # the next flag tells us when we are in flow_function arguments
        flow_functions_argument_found = False
        for parameter in all_parameters:
            if not is_parameter_subclass_type(parameter, FlowFunction):
                if flow_functions_argument_found:
                    raise AssertionError(
                        "flow has to have all non-flow-function arguments before flow function arguments."
                    )
                if parameter.name in flow_functions_configuration:
                    raise AssertionError(
                        f"Argument `{parameter.name}` in flow `{wrapped_flow.__name__}`"
                        f" is not FlowFunction and"
                        f" is also present in the flow configuration."
                        f" Arguments that are not FlowFunction cannot be present in the flow configuration."
                    )
                non_flow_functions_parameters.append(parameter)
                continue

            flow_functions_argument_found = True

            if is_parameter_subclass_type(parameter, FlowArgument):
                if isinstance(parameter.default, FlowArgument):
                    parameter.default.name = parameter.name
                non_flow_functions_parameters.append(parameter)
                flow_function_arguments.add(parameter.name)

            flow_functions_parameters.append(parameter)

        flow_functions_argument_parameters_without_default: list[inspect.Parameter] = []
        flow_functions_argument_parameters_with_default: list[inspect.Parameter] = []
        non_flow_function_arguments: list[
            FlowArgument[Any]
        ] = []  # Argument in configuration that are not flow argument
        for (
            flow_function_name,
            flow_function_configuration,
        ) in flow_functions_configuration.items():
            if not isinstance(flow_function_configuration, FlowArgument):
                continue

            flow_function_configuration.name = flow_function_name

            if flow_function_name in flow_function_arguments:
                if (
                    flow_function_configuration.value_or_empty
                    == inspect.Parameter.empty
                ):
                    continue
                argument_index = -1
                for index, parameter in enumerate(non_flow_functions_parameters):
                    if parameter.name == flow_function_name:
                        argument_index = index
                        break
                if argument_index == -1:
                    continue
                parameter = non_flow_functions_parameters[argument_index]
                non_flow_functions_parameters[argument_index] = inspect.Parameter(
                    name=parameter.name,
                    kind=parameter.kind,
                    annotation=parameter.annotation,
                    default=flow_function_configuration.value,
                )
                continue

            non_flow_function_arguments.append(flow_function_configuration)
            new_parameter = inspect.Parameter(
                name=flow_function_name,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=flow_function_configuration.value_or_empty,
                annotation=flow_function_configuration.argument_type,
            )
            if flow_function_configuration.value_or_empty is inspect.Parameter.empty:
                flow_functions_argument_parameters_without_default.append(new_parameter)
            else:
                flow_functions_argument_parameters_with_default.append(new_parameter)

        @with_signature(
            func_name=wrapped_flow.__name__,
            func_signature=inspect.Signature(
                flow_functions_argument_parameters_without_default
                + non_flow_functions_parameters
                + flow_functions_argument_parameters_with_default
            ),
        )
        def flow_invoker(**kwargs: Any) -> ReturnType:
            flow_context = FlowContext()

            for configured_flow_function in flow_functions_configuration:
                flow_context[configured_flow_function] = FlowFunctionInvoker(
                    flow_function=flow_functions_configuration[
                        configured_flow_function
                    ],
                    flow_context=flow_context,
                )

            missing_flow_arguments: list[str] = []
            for flow_function_parameter in flow_functions_parameters:
                if (
                    flow_function_parameter.name not in flow_context
                    and flow_function_parameter.default is inspect.Parameter.empty
                    and flow_function_parameter.name not in kwargs
                ):
                    missing_flow_arguments.append(flow_function_parameter.name)
                    continue

                if flow_function_parameter.name in kwargs:
                    if not isinstance(
                        kwargs[flow_function_parameter.name], FlowFunction
                    ):
                        kwargs[flow_function_parameter.name] = FlowArgument(
                            get_args(flow_function_parameter.annotation)[0],
                            default=kwargs[flow_function_parameter.name],
                        )
                    flow_context[flow_function_parameter.name] = FlowFunctionInvoker(
                        flow_function=kwargs[flow_function_parameter.name],
                        flow_context=flow_context,
                    )
                    kwargs[flow_function_parameter.name] = flow_context[
                        flow_function_parameter.name
                    ]

                else:
                    if flow_function_parameter.default is not inspect.Parameter.empty:
                        default_parameter_invoker = FlowFunctionInvoker(
                            flow_function=flow_function_parameter.default,
                            flow_context=flow_context,
                        )
                        if flow_function_parameter.name not in flow_context:
                            flow_context[flow_function_parameter.name] = (
                                default_parameter_invoker
                            )
                        kwargs[flow_function_parameter.name] = default_parameter_invoker
                    else:
                        kwargs[flow_function_parameter.name] = flow_context[
                            flow_function_parameter.name
                        ]

            if len(missing_flow_arguments) > 0:
                raise AssertionError(
                    f"`{'`, `'.join(missing_flow_arguments)}`"
                    f" {'FlowFunction is' if len(missing_flow_arguments) == 1 else 'FlowFunctions are'}"
                    f" required by the flow `{wrapped_flow.__name__}`"
                    f" but {'is' if len(missing_flow_arguments) == 1 else 'are'}"
                    f" missing in the flow context."
                )

            for non_flow_function_argument in non_flow_function_arguments:
                if non_flow_function_argument.name in kwargs:
                    non_flow_function_argument.value = kwargs[
                        non_flow_function_argument.name
                    ]
                    flow_context[non_flow_function_argument.name] = FlowFunctionInvoker(
                        flow_function=non_flow_function_argument,
                        flow_context=flow_context,
                    )
                    del kwargs[non_flow_function_argument.name]

            return wrapped_flow(**kwargs)

        return flow_invoker

    return wrapper
