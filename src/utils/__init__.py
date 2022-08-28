"""General-Purpose Utils."""

import types as ty
import typing as tp


def init_obj(
    module: ty.ModuleType,
    obj_name: str,
    *args: tp.Optional[tp.Any],
    **kwargs: tp.Optional[tp.Any],
) -> tp.Any:
    """Initialize an object defined in a module with parameters if specified.

    Args:
        module (ModuleType): Name of the module.
        obj_name (str): Name of the object.
        *args (Any, optional): Variable length arguments.
        **kwargs (Any, optional): Arbitrary keyword arguments.

    Returns:
        Object defined in a module.
    """
    return getattr(module, obj_name)(*args, **kwargs)
