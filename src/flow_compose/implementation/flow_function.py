# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import inspect
from functools import cached_property
from typing import Callable, Any, Generic, Type
from typing import get_origin

from extensions.makefun_extension import with_signature
from flow_compose.types import ReturnType


class FlowContext(dict[str, "FlowFunctionInvoker[Any]"]):
    pass


_EMPTY_FLOW_CONTEXT = FlowContext()


class FlowFunction(Generic[ReturnType]):
    def __init__(self, flow_function: Callable[..., ReturnType], cached: bool):
        self._flow_function = flow_function
        self._flow_function_signature = inspect.signature(flow_function)
        self.cached = cached

    def __call__(self, *args: Any, **kwargs: Any) -> ReturnType:
        return self._flow_function(*args, **kwargs)

    @property
    def name(self) -> str:
        return self._flow_function.__name__

    @cached_property
    def parameters(self) -> list[inspect.Parameter]:
        return [p for p in self._flow_function_signature.parameters.values()]


def annotation(cached: bool = False) -> Callable[..., FlowFunction[ReturnType]]:
    def wrapper(
        wrapped_flow_function: Callable[..., ReturnType],
    ) -> FlowFunction[ReturnType]:
        all_parameters = inspect.signature(wrapped_flow_function).parameters.values()
        flow_functions_parameters = []
        non_flow_functions_parameters = []

        # the next flag tells us when we are in flow_function arguments
        flow_functions_argument_found = False
        for parameter in all_parameters:
            parameter_origin = get_origin(parameter.annotation)
            is_parameter_flow_function = (
                FlowFunction == parameter_origin
                or FlowFunction == parameter.annotation
                or isinstance(parameter.default, FlowFunction)
            )
            if not is_parameter_flow_function:
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
                        name="flow_context",
                        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=FlowContext,
                        default=_EMPTY_FLOW_CONTEXT,
                    )
                ]
            ),
        )
        def flow_function_with_flow_context(
            flow_context: FlowContext, *args: Any, **kwargs: Any
        ) -> ReturnType:
            missing_flow_function_configurations: list[str] = []
            for parameter in flow_functions_parameters:
                if (
                    not isinstance(parameter.default, FlowFunction)
                    and parameter.name not in flow_context
                ):
                    missing_flow_function_configurations.append(parameter.name)
                    continue

                kwargs[parameter.name] = (
                    parameter.default
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


class Argument(FlowFunction[ReturnType], Generic[ReturnType]):
    def __init__(
        self,
        argument_type: Type[ReturnType],
        value: ReturnType | Any = inspect.Parameter.empty,
    ) -> None:
        self.__value = value
        self.__name: str | None = None
        self._argument_type = argument_type
        super().__init__(
            flow_function=lambda: self.value,
            cached=False,
        )

    def __call__(self) -> ReturnType:
        return self.value

    @property
    def value_or_empty(self) -> ReturnType | Any:
        return self.__value

    @property
    def value(self) -> ReturnType:
        assert self.__value is not inspect.Parameter.empty
        assert isinstance(self.__value, self.argument_type)
        return self.__value

    @value.setter
    def value(self, value: ReturnType) -> None:
        self.__value = value

    @property
    def name(self) -> str:
        assert self.__name is not None
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        self.__name = name

    @property
    def parameters(self) -> list[inspect.Parameter]:
        return []

    @property
    def argument_type(self) -> Type[ReturnType]:
        return self._argument_type


class FlowFunctionInvoker(Generic[ReturnType]):
    def __init__(
        self,
        flow_function: FlowFunction[ReturnType],
        flow_context: FlowContext,
    ) -> None:
        self._flow_function = flow_function
        self._flow_context = flow_context
        self._flow_function_cache: dict[int, ReturnType] = {}

    def __call__(self, *args: Any, **kwargs: Any) -> ReturnType:
        if not self._flow_function.cached:
            if not isinstance(self._flow_function, Argument):
                kwargs["flow_context"] = self._flow_context
            return self._flow_function(*args, **kwargs)

        values_for_hash = tuple(v for v in args + tuple(kwargs.values()))
        cache_hash = hash(values_for_hash)
        if cache_hash in self._flow_function_cache:
            return self._flow_function_cache[cache_hash]

        kwargs["flow_context"] = self._flow_context

        result = self._flow_function(*args, **kwargs)

        self._flow_function_cache[cache_hash] = result

        return result
