__all__ = (
    "enforcer", "type_enforce",
)

class Enforcer(object):
    __slots__ = ("exc",)
    
    def __init__(self, exc):
        self.exc = exc
    
    def __call__(self, cond, *args, **kwargs):
        if not cond:
            raise self.exc(*args, **kwargs)


@ft.lru_cache()
def enforcer(exc):
    return Enforcer(exc)

type_enforce = enforcer(TypeError)
