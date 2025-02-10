# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import inspect
from functools import cached_property
from typing import TypeVar, Callable, Any, Generic

ReturnType = TypeVar("ReturnType")


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


class FlowContext(dict[str, "FlowFunctionInvoker[Any]"]):
    pass


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
