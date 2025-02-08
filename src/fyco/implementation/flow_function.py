# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
from typing import Callable, Any

from fyco.types import ReturnType


def annotation(wrapped: Callable[..., ReturnType]) -> ReturnType:
    def flow_function(**kwargs: Any) -> ReturnType:
        return wrapped(**kwargs)

    return flow_function
