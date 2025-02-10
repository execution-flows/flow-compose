# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import inspect
from functools import cached_property
from typing import TypeVar, Callable, Any, Generic, cast

ReturnType = TypeVar("ReturnType")


class FlowFunction(Generic[ReturnType]):
    def __init__(self, flow_function: Callable[..., ReturnType], cached: bool):
        self._flow_function = flow_function
        self._flow_function_signature = inspect.signature(flow_function)
        self.cached = cached
        self._flow_function_cache: dict[int, dict[int, ReturnType]] = {}

    def __call__(self, *args: Any, **kwargs: Any) -> ReturnType:
        if not self.cached:
            return self._flow_function(*args, **kwargs)

        flow_run_id = cast(FlowContext, kwargs["flow_context"]).flow_run_id
        kwargs_values_list_without_flow_context = map(
            lambda kwarg: kwarg[1],
            filter(
                lambda kwarg: kwarg[0] != "flow_context",
                kwargs.items(),
            ),
        )
        values_for_hash = tuple(
            v for v in args + tuple(kwargs_values_list_without_flow_context)
        )
        cache_hash = hash(values_for_hash)
        if (
            flow_run_id in self._flow_function_cache
            and cache_hash in self._flow_function_cache[flow_run_id]
        ):
            return self._flow_function_cache[flow_run_id][cache_hash]

        result = self._flow_function(*args, **kwargs)
        if flow_run_id not in self._flow_function_cache:
            self._flow_function_cache[flow_run_id] = {}
        self._flow_function_cache[flow_run_id][cache_hash] = result
        return result

    def reset_cache(self, flow_run_id: int) -> None:
        if flow_run_id in self._flow_function_cache:
            del self._flow_function_cache[flow_run_id]

    @property
    def name(self) -> str:
        return self._flow_function.__name__

    @cached_property
    def parameters(self) -> list[inspect.Parameter]:
        return [p for p in self._flow_function_signature.parameters.values()]


class FlowContext(dict[str, FlowFunction[Any]]):
    flow_run_id: int

    def __init__(self, flow_run_id: int, **kwargs: Any):
        self.flow_run_id = flow_run_id
        super().__init__(**kwargs)
