"""
The class pypystm.hashtable, mapping integers to objects.
"""

from pypy.interpreter.baseobjspace import W_Root
from pypy.interpreter.typedef import TypeDef
from pypy.interpreter.gateway import interp2app, unwrap_spec, WrappedDefault

from rpython.rlib import rstm
from rpython.rtyper.annlowlevel import cast_gcref_to_instance
from rpython.rtyper.annlowlevel import cast_instance_to_gcref


class W_Hashtable(W_Root):

    def __init__(self):
        self.h = rstm.create_hashtable()

    @unwrap_spec(key=int)
    def getitem_w(self, space, key):
        gcref = self.h.get(key)
        if not gcref:
            space.raise_key_error(space.wrap(key))
        return cast_gcref_to_instance(W_Root, gcref)

    @unwrap_spec(key=int)
    def setitem_w(self, key, w_value):
        entry = self.h.lookup(key)
        entry.object = cast_instance_to_gcref(w_value)

    @unwrap_spec(key=int)
    def delitem_w(self, space, key):
        entry = self.h.lookup(key)
        if not entry.object:
            space.raise_key_error(space.wrap(key))
        entry.object = rstm.NULL_GCREF

    @unwrap_spec(key=int)
    def contains_w(self, space, key):
        gcref = self.h.get(key)
        return space.newbool(not not gcref)

    @unwrap_spec(key=int, w_default=WrappedDefault(None))
    def get_w(self, space, key, w_default):
        gcref = self.h.get(key)
        if not gcref:
            return w_default
        return cast_gcref_to_instance(W_Root, gcref)

    @unwrap_spec(key=int, w_default=WrappedDefault(None))
    def setdefault_w(self, space, key, w_default):
        entry = self.h.lookup(key)
        gcref = entry.object
        if not gcref:
            entry.object = cast_instance_to_gcref(w_default)
            return w_default
        return cast_gcref_to_instance(W_Root, gcref)


def W_Hashtable___new__(space, w_subtype):
    r = space.allocate_instance(W_Hashtable, w_subtype)
    r.__init__()
    return space.wrap(r)

W_Hashtable.typedef = TypeDef(
    'pypystm.hashtable',
    __new__ = interp2app(W_Hashtable___new__),
    __getitem__ = interp2app(W_Hashtable.getitem_w),
    __setitem__ = interp2app(W_Hashtable.setitem_w),
    __delitem__ = interp2app(W_Hashtable.delitem_w),
    __contains__ = interp2app(W_Hashtable.contains_w),
    get = interp2app(W_Hashtable.get_w),
    setdefault = interp2app(W_Hashtable.setdefault_w),
    )
