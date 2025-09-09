# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
from typing import Generic, Any

from flow_compose.implementation.classes.flow_function import FlowFunction
from flow_compose.implementation.classes import base
from flow_compose.implementation.classes.flow_argument import FlowArgument
from flow_compose.types import ReturnType


class FlowFunctionInvoker(
    base.FlowFunctionInvoker[FlowFunction[ReturnType], ReturnType], Generic[ReturnType]
):
    def __call__(self, *args: Any, **kwargs: Any) -> ReturnType:
        if not self._flow_function.cached:
            if not isinstance(self._flow_function, FlowArgument):
                kwargs["__flow_context"] = self._flow_context
            return self._flow_function(*args, **kwargs)

        values_for_hash = tuple(v for v in args + tuple(kwargs.values()))
        cache_hash = hash(values_for_hash)
        if cache_hash in self._flow_function_cache:
            return self._flow_function_cache[cache_hash]

        kwargs["__flow_context"] = self._flow_context

        result = self._flow_function(*args, **kwargs)

        self._flow_function_cache[cache_hash] = result

        return result
