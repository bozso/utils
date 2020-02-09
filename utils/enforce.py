__all__ = (
    "Enforcer",
)

class Enforcer(object):
    def enforce(self, cond, *args, **kwargs):
        if not cond:
            raise self(*args, **kwargs)

class TypeEnforce(TypeError, Enforcer):
    pass
