from functools import partial

__all__ = (
    "enforce", "type_enforce",
)

def enforce(cond, *args, **kwargs):
    exc = kwargs.pop("exception", Exception)
    
    if not cond:
        raise exc(*args, **kwargs)

type_enforce = partial(enforce, exception=TypeError)
