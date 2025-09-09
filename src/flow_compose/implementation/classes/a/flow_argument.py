# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
from typing import Generic

from flow_compose.implementation.classes import base
from flow_compose.implementation.classes.a.flow_function import FlowFunction
from flow_compose.types import ReturnType


class FlowArgument(
    base.FlowArgument[ReturnType], FlowFunction[ReturnType], Generic[ReturnType]
):
    async def __call__(self) -> ReturnType:
        return self.value
