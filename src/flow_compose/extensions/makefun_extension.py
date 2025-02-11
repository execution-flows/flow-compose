# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.


from inspect import Signature
from typing import cast, Callable, Any, Union, Dict

import makefun


# This method just has plain wrong typing -
#  it declares an argument as a str and then assigns it a default None
def with_signature(
    func_signature: Union[str, Signature],
    func_name: str | None = None,
    inject_as_first_arg: bool = False,
    add_source: bool = True,
    add_impl: bool = True,
    doc: str | None = None,
    qualname: str | None = None,
    co_name: str | None = None,
    module_name: str | None = None,
    **attrs: Dict[str, Any],
) -> Callable[..., Callable[..., Any]]:
    return cast(
        Callable[..., Callable[..., Any]],
        makefun.with_signature(
            func_signature,
            func_name,
            inject_as_first_arg,
            add_source,
            add_impl,
            doc,
            qualname,
            co_name,
            module_name,
            **attrs,
        ),
    )
