# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import inspect
from typing import Generic, Any

from flow_compose.implementation.classes.flow_function import FlowFunction
from flow_compose.types import ReturnType


class FlowArgument(FlowFunction[ReturnType], Generic[ReturnType]):
    def __init__(
        self,
        argument_type: type[ReturnType],
        default: ReturnType | Any = inspect.Parameter.empty,
    ) -> None:
        self.__default = default
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
        return self.__default

    @property
    def value(self) -> ReturnType:
        assert self.__default is not inspect.Parameter.empty
        return self.__default

    @value.setter
    def value(self, value: ReturnType) -> None:
        self.__default = value

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
    def argument_type(self) -> type[ReturnType]:
        return self._argument_type
